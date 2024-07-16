import json
from pathlib import Path
from typing import List

import napari
import tifffile
from brainglobe_atlasapi import BrainGlobeAtlas
from brainglobe_space import AnatomicalSpace
from qtpy import QtCore
from qtpy.QtCore import QAbstractTableModel, Qt
from qtpy.QtWidgets import (
    QComboBox,
    QFileDialog,
    QGridLayout,
    QLabel,
    QTableView,
    QWidget,
)

from brainglobe_utils.brainmapper.analysis import (
    summarise_points_by_atlas_region,
)
from brainglobe_utils.brainreg.transform import (
    transform_points_from_downsampled_to_atlas_space,
)
from brainglobe_utils.qtpy.dialog import display_info
from brainglobe_utils.qtpy.interaction import add_button, add_combobox
from brainglobe_utils.qtpy.logo import header_widget


class TransformPoints(QWidget):
    def __init__(self, viewer: napari.viewer.Viewer):
        super(TransformPoints, self).__init__()
        self.viewer = viewer
        self.raw_data = None
        self.points_layer = None
        self.atlas = None
        self.transformed_points = None

        self.image_layer_names = self._get_layer_names()
        self.points_layer_names = self._get_layer_names(
            layer_type=napari.layers.Points
        )
        self.setup_main_layout()

        @self.viewer.layers.events.connect
        def update_layer_list(v: napari.viewer.Viewer):
            """
            Update internal list of layers whenever the napari layers list
            is updated.
            """
            self.image_layer_names = self._get_layer_names()
            self.points_layer_names = self._get_layer_names(
                layer_type=napari.layers.Points
            )

            self._update_combobox_options(
                self.raw_data_choice, self.image_layer_names
            )

            self._update_combobox_options(
                self.points_layer_choice, self.points_layer_names
            )

    @staticmethod
    def _update_combobox_options(combobox: QComboBox, options_list: List[str]):
        original_text = combobox.currentText()
        combobox.clear()
        combobox.addItems(options_list)
        combobox.setCurrentText(original_text)

    def _get_layer_names(
        self,
        layer_type: napari.layers.Layer = napari.layers.Image,
        default: str = "",
    ) -> List[str]:
        """
        Get list of layer names of a given layer type.
        """
        layer_names = [
            layer.name
            for layer in self.viewer.layers
            if type(layer) == layer_type
        ]

        if layer_names:
            return [default] + layer_names
        else:
            return [default]

    def setup_main_layout(self):
        self.layout = QGridLayout()
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setAlignment(QtCore.Qt.AlignTop)
        self.layout.setSpacing(4)
        self.add_header()
        self.add_points_combobox(row=1, column=0)
        self.add_raw_data_combobox(row=2, column=0)
        self.add_transform_button(row=3, column=0)
        self.add_analyse_button(row=3, column=1)

        self.add_points_summary_table(row=4, column=0)
        self.add_save_all_points_button(row=6, column=0)
        self.add_save_points_summary_button(row=6, column=1)
        self.add_status_label(row=7, column=0)

        self.setLayout(self.layout)

    def add_header(self):
        """
        Header including brainglobe logo and documentation links.
        """
        # <br> is included in the package_name to make the label under the logo
        # more compact, by splitting it onto two lines
        header = header_widget(
            package_name="brainglobe-<br>utils",
            package_tagline="Transform points to atlas space",
            github_repo_name="brainglobe-utils",
            citation_doi="https://doi.org/10.1038/s41598-021-04676-9",
            help_text="For help, hover the cursor over each parameter.",
        )
        self.layout.addWidget(header, 0, 0, 1, 2)

    def add_points_combobox(self, row, column):
        self.points_layer_choice, _ = add_combobox(
            self.layout,
            "Points layer",
            self.points_layer_names,
            column=column,
            row=row,
            callback=self.set_points_layer,
        )

    def add_raw_data_combobox(self, row, column):
        self.raw_data_choice, _ = add_combobox(
            self.layout,
            "Raw data layer",
            self.image_layer_names,
            column=column,
            row=row,
            callback=self.set_raw_data_layer,
        )

    def add_transform_button(self, row, column):
        self.transform_button = add_button(
            "Transform points",
            self.layout,
            self.transform_points_to_atlas_space,
            row=row,
            column=column,
            visibility=True,
            tooltip="Transform points layer to atlas space",
        )

    def add_analyse_button(self, row, column):
        self.analyse_button = add_button(
            "Analyse points",
            self.layout,
            self.analyse_points,
            row=row,
            column=column,
            visibility=False,
            tooltip="Analyse distribution of points within the atlas",
        )

    def add_points_summary_table(self, row, column):
        self.points_per_region_table_title = QLabel(
            "Points distribution summary"
        )
        self.points_per_region_table_title.setVisible(False)
        self.layout.addWidget(self.points_per_region_table_title, row, column)
        self.points_per_region_table = QTableView()
        self.points_per_region_table.setVisible(False)
        self.layout.addWidget(self.points_per_region_table, row + 1, column)

    def add_save_all_points_button(self, row, column):
        self.save_all_points_button = add_button(
            "Save all points information",
            self.layout,
            self.save_all_points_csv,
            row=row,
            column=column,
            visibility=False,
            tooltip="Save all points information as a csv file",
        )

    def add_save_points_summary_button(self, row, column):
        self.save_points_summary_button = add_button(
            "Save points summary",
            self.layout,
            self.save_points_summary_csv,
            row=row,
            column=column,
            visibility=False,
            tooltip="Save points summary as a csv file",
        )

    def add_status_label(self, row, column):
        self.status_label = QLabel()
        self.status_label.setText("Ready")
        self.layout.addWidget(self.status_label, row, column)

    def set_raw_data_layer(self):
        """
        Set background layer from current background text box selection.
        """
        if self.raw_data_choice.currentText() != "":
            self.raw_data = self.viewer.layers[
                self.raw_data_choice.currentText()
            ]

    def set_points_layer(self):
        """
        Set background layer from current background text box selection.
        """
        if self.points_layer_choice.currentText() != "":
            self.points_layer = self.viewer.layers[
                self.points_layer_choice.currentText()
            ]

    def transform_points_to_atlas_space(self):
        layers_in_place = self.check_layers()
        if not layers_in_place:
            return

        self.status_label.setText("Loading brainreg data ...")
        self.load_brainreg_directory()
        self.status_label.setText("Transforming points ...")

        self.run_transform_points_to_downsampled_space()
        self.run_transform_downsampled_points_to_atlas_space()
        self.analyse_button.setVisible(True)
        self.status_label.setText("Ready")

    def check_layers(self):
        if self.raw_data is None and self.points_layer is None:
            display_info(
                self,
                "No layers selected",
                "Please select the layers corresponding to the points "
                "you would like to transform and the raw data (registered by "
                "brainreg)",
            )
            return False

        if self.raw_data is None:
            display_info(
                self,
                "No raw data layer selected",
                "Please select a layer that corresponds to the raw "
                "data (registered by brainreg)",
            )
            return False

        if self.points_layer is None:
            display_info(
                self,
                "No points layer selected",
                "Please select a points layer you would like to transform",
            )
            return False

        return True

    def load_brainreg_directory(self):
        brainreg_directory = QFileDialog.getExistingDirectory(
            self,
            "Select brainreg directory",
        )
        if not brainreg_directory:
            return
        else:
            self.brainreg_directory = Path(brainreg_directory)

        self.get_brainreg_paths()
        self.check_brainreg_directory()
        self.get_registration_metadata()
        self.load_atlas()
        self.status_label.setText("Ready")

    def get_brainreg_paths(self):
        self.paths = self.Paths(self.brainreg_directory)

    def check_brainreg_directory(self):
        try:
            with open(self.paths.brainreg_metadata_file) as json_file:
                self.brainreg_metadata = json.load(json_file)

                if not self.brainreg_metadata["atlas"]:
                    self.display_directory_warning()

        except FileNotFoundError:
            self.display_directory_warning()

    def display_directory_warning(self):
        display_info(
            self,
            "Not a brainreg directory",
            "This directory does not appear to be a valid brainreg "
            "directory. Please try loading another brainreg output directory.",
        )

    def get_registration_metadata(self):
        self.metadata = self.Metadata(self.brainreg_metadata)

    def load_atlas(self):
        self.atlas = BrainGlobeAtlas(self.metadata.atlas_string)

    def run_transform_points_to_downsampled_space(self):
        downsampled_space = self.get_downsampled_space()
        source_space = self.get_source_space()
        self.points_in_downsampled_space = source_space.map_points_to(
            downsampled_space, self.points_layer.data
        )
        self.viewer.add_points(
            self.points_in_downsampled_space,
            name="Points in downsampled space",
            visible=False,
        )

    def run_transform_downsampled_points_to_atlas_space(self):
        deformation_field_paths = [
            self.paths.deformation_field_0,
            self.paths.deformation_field_1,
            self.paths.deformation_field_2,
        ]
        self.points_in_atlas_space, points_out_of_bounds = (
            transform_points_from_downsampled_to_atlas_space(
                self.points_in_downsampled_space,
                self.atlas,
                deformation_field_paths,
                warn_out_of_bounds=False,
            )
        )
        self.viewer.add_points(
            self.points_in_atlas_space,
            name="Points in atlas space",
            visible=True,
        )

        if len(points_out_of_bounds) > 0:
            display_info(
                self,
                "Points outside atlas",
                f"{len(points_out_of_bounds)} fell outside the atlas space",
            )

    def get_downsampled_space(self):
        target_shape = tifffile.imread(self.paths.downsampled_image).shape

        downsampled_space = AnatomicalSpace(
            self.atlas.orientation,
            shape=target_shape,
            resolution=self.atlas.resolution,
        )
        return downsampled_space

    def get_source_space(self):
        source_space = AnatomicalSpace(
            self.metadata.orientation,
            shape=self.raw_data.data.shape,
            resolution=[float(i) for i in self.metadata.voxel_sizes],
        )
        return source_space

    def analyse_points(self):
        self.all_points_df, self.points_per_region_df = (
            summarise_points_by_atlas_region(
                self.points_layer.data,
                self.points_in_atlas_space,
                self.atlas,
                self.paths.volume_csv_path,
            )
        )

        self.populate_summary_table()
        self.save_all_points_button.setVisible(True)
        self.save_points_summary_button.setVisible(True)

        print("Analysing points")

    def populate_summary_table(
        self,
        columns_to_keep=[
            "structure_name",
            "left_cell_count",
            "right_cell_count",
        ],
    ):
        summary_df = self.points_per_region_df[columns_to_keep]
        self.points_per_region_table_model = DataFrameModel(summary_df)
        self.points_per_region_table.setModel(
            self.points_per_region_table_model
        )
        self.points_per_region_table_title.setVisible(True)
        self.points_per_region_table.setVisible(True)

    def save_all_points_csv(self):
        self.all_points_csv_path, _ = QFileDialog.getSaveFileName(
            self,
            "Choose filename",
            "",
            "CSV Files (*.csv)",
        )
        self.all_points_csv_path = ensure_extension(
            self.all_points_csv_path, ".csv"
        )
        self.all_points_df.to_csv(self.all_points_csv_path, index=False)

    def save_points_summary_csv(self):
        self.summary_points_csv_path, _ = QFileDialog.getSaveFileName(
            self,
            "Choose filename",
            "",
            "CSV Files (*.csv)",
        )
        self.summary_points_csv_path = ensure_extension(
            self.summary_points_csv_path, ".csv"
        )
        self.points_per_region_df.to_csv(
            self.summary_points_csv_path, index=False
        )

    class Paths:
        """
        A single class to hold all file paths that may be used.
        """

        def __init__(self, brainreg_directory):
            self.brainreg_directory = brainreg_directory
            self.brainreg_metadata_file = self.make_filepaths("brainreg.json")
            self.deformation_field_0 = self.make_filepaths(
                "deformation_field_0.tiff"
            )
            self.deformation_field_1 = self.make_filepaths(
                "deformation_field_1.tiff"
            )
            self.deformation_field_2 = self.make_filepaths(
                "deformation_field_2.tiff"
            )
            self.downsampled_image = self.make_filepaths("downsampled.tiff")
            self.volume_csv_path = self.make_filepaths("volumes.csv")

        def make_filepaths(self, filename):
            return self.brainreg_directory / filename

    class Metadata:
        def __init__(self, brainreg_metadata):
            self.orientation = brainreg_metadata["orientation"]
            self.atlas_string = brainreg_metadata["atlas"]
            self.voxel_sizes = brainreg_metadata["voxel_sizes"]


class DataFrameModel(QAbstractTableModel):
    def __init__(self, df):
        super().__init__()
        self._df = df

    def rowCount(self, parent=None):
        return self._df.shape[0]

    def columnCount(self, parent=None):
        return self._df.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return str(self._df.iloc[index.row(), index.column()])
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self._df.columns[section]
            if orientation == Qt.Vertical:
                return self._df.index[section]
        return None


def ensure_extension(file_path, extension):
    path = Path(file_path)
    if path.suffix != extension:
        path = path.with_suffix(extension)
    return path
