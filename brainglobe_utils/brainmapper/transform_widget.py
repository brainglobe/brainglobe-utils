import json
from pathlib import Path
from typing import Any, Dict, List, Union

import napari
import pandas as pd
import tifffile
from brainglobe_atlasapi import BrainGlobeAtlas
from brainglobe_atlasapi.list_atlases import get_downloaded_atlases
from brainglobe_space import AnatomicalSpace
from qtpy import QtCore
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
from brainglobe_utils.brainmapper.export import export_points_to_brainrender
from brainglobe_utils.brainreg.transform import (
    transform_points_from_downsampled_to_atlas_space,
)
from brainglobe_utils.general.system import ensure_extension
from brainglobe_utils.qtpy.dialog import display_info
from brainglobe_utils.qtpy.interaction import add_button, add_combobox
from brainglobe_utils.qtpy.logo import header_widget
from brainglobe_utils.qtpy.table import DataFrameModel


class TransformPoints(QWidget):
    def __init__(self, viewer: napari.viewer.Viewer):
        """
        Initialize the TransformPoints widget.

        Parameters
        ----------
        viewer : napari.viewer.Viewer
            The napari viewer instance.
            This will be passed when opening the widget.
        """
        super(TransformPoints, self).__init__()
        self.viewer = viewer
        self.raw_data = None
        self.points_layer = None
        self.atlas = None
        self.transformed_points = None

        self.image_layer_names = self._get_layer_names(
            layer_type=napari.layers.Image
        )
        self.points_layer_names = self._get_layer_names(
            layer_type=napari.layers.Points
        )
        self.setup_main_layout()

        @self.viewer.layers.events.connect
        def update_layer_list(v: napari.viewer.Viewer) -> None:
            """
            Update internal list of layers whenever the napari layers list
            is updated.

            Parameters
            ----------
            v : napari.viewer.Viewer
                The napari viewer instance.
            """
            self.image_layer_names = self._get_layer_names(
                layer_type=napari.layers.Image
            )
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
    def _update_combobox_options(
        combobox: QComboBox, options_list: List[str]
    ) -> None:
        """
        Update the options in a QComboBox.

        Parameters
        ----------
        combobox : QComboBox
            The combobox to update.
        options_list : List[str]
            The list of options to set in the combobox.
        """

        original_text = combobox.currentText()
        combobox.clear()
        combobox.addItems(options_list)
        combobox.setCurrentText(original_text)

    def _get_layer_names(
        self,
        layer_type: napari.layers.Layer,
        default: str = "",
    ) -> List[str]:
        """
        Get list of layer names of a given layer type.

        Parameters
        ----------
        layer_type : napari.layers.Layer, optional
            The type of layer to get names for.
        default : str, optional
            Default values to include in the list. Default is an empty string.

        Returns
        -------
        List[str]
            A list of layer names.
        """
        layer_names = [
            layer.name
            for layer in self.viewer.layers
            if isinstance(layer, layer_type)
        ]

        if layer_names:
            return [default] + layer_names
        else:
            return [default]

    def setup_main_layout(self) -> None:
        """
        Set up the main layout of the widget.
        """
        self.layout = QGridLayout()
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setAlignment(QtCore.Qt.AlignTop)
        self.layout.setSpacing(4)
        self.add_header()
        self.add_points_combobox(row=1, column=0)
        self.add_raw_data_combobox(row=2, column=0)
        self.add_transform_button(row=3, column=0)
        self.add_brainrender_export_button(row=3, column=1)
        self.add_points_summary_table(row=4, column=0)
        self.add_save_all_points_button(row=6, column=0)
        self.add_save_points_summary_button(row=6, column=1)
        self.add_status_label(row=7, column=0)

        self.setLayout(self.layout)

    def add_header(self) -> None:
        """
        Header including brainglobe logo and documentation links.
        """
        header = header_widget(
            package_name="brainmapper",
            package_tagline="Transform points to atlas space",
            github_repo_name="brainglobe-utils",
            citation_doi="https://doi.org/10.1371/journal.pcbi.1009074",
        )
        self.layout.addWidget(header, 0, 0, 1, 2)

    def add_points_combobox(self, row: int, column: int) -> None:
        """
        Add a combobox for selecting the points layer containing
        the points (e.g. cells) to transform to a BrainGlobe atlas.

        Parameters
        ----------
        row : int
            Row in the grid layout.
        column : int
            Column in the grid layout.
        """
        self.points_layer_choice, _ = add_combobox(
            self.layout,
            "Points layer",
            self.points_layer_names,
            column=column,
            row=row,
            callback=self.set_points_layer,
        )

    def add_raw_data_combobox(self, row: int, column: int) -> None:
        """
        Add a combobox for selecting the raw data layer. This defines
        the coordinate space for transforming points to a BrainGlobe atlas.

        Parameters
        ----------
        row : int
            Row in the grid layout.
        column : int
            Column in the grid layout.
        """
        self.raw_data_choice, _ = add_combobox(
            self.layout,
            "Raw data layer",
            self.image_layer_names,
            column=column,
            row=row,
            callback=self.set_raw_data_layer,
        )

    def add_transform_button(self, row: int, column: int) -> None:
        """
        Add a button to begin the transformation of points to atlas space.

        Parameters
        ----------
        row : int
            Row in the grid layout.
        column : int
            Column in the grid layout.
        """
        self.transform_button = add_button(
            "Transform points",
            self.layout,
            self.transform_points_to_atlas_space,
            row=row,
            column=column,
            visibility=True,
            tooltip="Transform points layer to atlas space",
        )

    def add_brainrender_export_button(self, row: int, column: int) -> None:
        """
        Add a button to export the points in atlas space in the brainrender
        format.

        Parameters
        ----------
        row : int
            Row in the grid layout.
        column : int
            Column in the grid layout.
        """
        self.brainrender_export_button = add_button(
            "Export to brainrender",
            self.layout,
            self.export_points_to_brainrender,
            row=row,
            column=column,
            visibility=False,
            tooltip="Export points in atlas space to brainrender",
        )

    def add_points_summary_table(self, row: int, column: int) -> None:
        """
        Add a table to display the summary of points per atlas region.

        Parameters
        ----------
        row : int
            Row in the grid layout.
        column : int
            Column in the grid layout.
        """
        self.points_per_region_table_title = QLabel(
            "Points distribution summary"
        )
        self.points_per_region_table_title.setVisible(False)
        self.layout.addWidget(self.points_per_region_table_title, row, column)
        self.points_per_region_table = QTableView()
        self.points_per_region_table.setVisible(False)
        self.layout.addWidget(self.points_per_region_table, row + 1, column)

    def add_save_all_points_button(self, row: int, column: int) -> None:
        """
        Add a button to save all points information (i.e. the list of
        all points, and their coordinates in raw data and atlas
        space, alongside assigned atlas region).

        Parameters
        ----------
        row : int
            Row in the grid layout.
        column : int
            Column in the grid layout.
        """
        self.save_all_points_button = add_button(
            "Save all points information",
            self.layout,
            self.save_all_points_csv,
            row=row,
            column=column,
            visibility=False,
            tooltip="Save all points information as a csv file",
        )

    def add_save_points_summary_button(self, row: int, column: int) -> None:
        """
        Add a button to save points summary (i.e. points per atlas region).

        Parameters
        ----------
        row : int
            Row in the grid layout.
        column : int
            Column in the grid layout.
        """
        self.save_points_summary_button = add_button(
            "Save points summary",
            self.layout,
            self.save_points_summary_csv,
            row=row,
            column=column,
            visibility=False,
            tooltip="Save points summary as a csv file",
        )

    def add_status_label(self, row: int, column: int) -> None:
        """
        Add a status label to inform the user of progress.

        Parameters
        ----------
        row : int
            Row in the grid layout.
        column : int
            Column in the grid layout.
        """
        self.status_label = QLabel()
        self.status_label.setText("Ready")
        self.layout.addWidget(self.status_label, row, column)

    def set_raw_data_layer(self) -> None:
        """
        Set background layer from current background text box selection.
        """
        if self.raw_data_choice.currentText() != "":
            self.raw_data = self.viewer.layers[
                self.raw_data_choice.currentText()
            ]

    def set_points_layer(self) -> None:
        """
        Set background layer from current background text box selection.
        """
        if self.points_layer_choice.currentText() != "":
            self.points_layer = self.viewer.layers[
                self.points_layer_choice.currentText()
            ]

    def transform_points_to_atlas_space(self) -> None:
        """
        Transform points layer to atlas space.
        """
        layers_in_place = self.check_layers()
        if not layers_in_place:
            return

        self.status_label.setText("Loading brainreg data ...")
        data_loaded = self.load_brainreg_directory()

        if not data_loaded:
            self.status_label.setText("Ready")
            return

        self.status_label.setText("Transforming points ...")

        self.run_transform_points_to_downsampled_space()
        self.run_transform_downsampled_points_to_atlas_space()

        self.status_label.setText("Analysing point distribution ...")
        self.analyse_points()
        self.status_label.setText("Ready")

    def check_layers(self) -> bool:
        """
        Check if the layers needed to begin the transformation
        have been selected by the user.

        Returns
        -------
        bool
            True if both raw data and points layers are selected,
            False otherwise.
        """
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

    def load_brainreg_directory(self) -> bool:
        """
        Load the brainreg directory selected by the user.
        Returns false if not selected, to abort analysis.

        Returns
        -------
        bool
            True if a directory was selected, False otherwise.
        """
        brainreg_directory = QFileDialog.getExistingDirectory(
            self,
            "Select brainreg directory",
        )
        if brainreg_directory == "":
            return False
        else:
            self.brainreg_directory = Path(brainreg_directory)

        self.initialise_brainreg_data()
        self.status_label.setText("Ready")
        return True

    def initialise_brainreg_data(self) -> None:
        """
        Initialize brainreg data by defining the paths,
        then loading the brainreg metadata, and then the atlas.
        """
        self.paths = Paths(self.brainreg_directory)
        self.check_brainreg_directory()
        self.metadata = Metadata(self.brainreg_metadata)
        self.load_atlas()

    def check_brainreg_directory(self) -> None:
        """
        Check if the selected directory is a valid brainreg directory
        by checking for the existence of an "atlas" entry in the json
        """
        try:
            with open(self.paths.brainreg_metadata_file) as json_file:
                self.brainreg_metadata = json.load(json_file)

                if "atlas" not in self.brainreg_metadata:
                    self.display_brainreg_directory_warning()

        except FileNotFoundError:
            self.display_brainreg_directory_warning()

    def display_brainreg_directory_warning(self) -> None:
        """
        Display a warning to the user if the selected directory
        is not a valid brainreg directory.
        """
        display_info(
            self,
            "Not a brainreg directory",
            "This directory does not appear to be a valid brainreg "
            "directory. Please try loading another brainreg output directory.",
        )

    def load_atlas(self) -> None:
        """
        Load the BrainGlobe atlas used for the initial brainreg registration.
        """
        if not self.is_atlas_installed(self.metadata.atlas_string):
            display_info(
                self,
                "Atlas not downloaded",
                f"Atlas: {self.metadata.atlas_string} needs to be "
                f"downloaded. This may take some time depending on "
                f"the size of the atlas and your network speed.",
            )
        self.atlas = BrainGlobeAtlas(self.metadata.atlas_string)

    def run_transform_points_to_downsampled_space(self) -> None:
        """
        Transform points fromm the raw data space (in which points
        were detected) to the downsampled space defined by brainreg.
        This space is the same as the raw data, but downsampled and realigned
        to match the orientation and resolution of the atlas.
        """
        downsampled_space = self.get_downsampled_space()
        raw_data_space = self.get_raw_data_space()
        self.points_in_downsampled_space = raw_data_space.map_points_to(
            downsampled_space, self.points_layer.data
        )
        self.viewer.add_points(
            self.points_in_downsampled_space,
            name="Points in downsampled space",
            visible=False,
        )

    def run_transform_downsampled_points_to_atlas_space(self) -> None:
        """
        Transform points from the downsampled space to atlas space. Uses
        the deformation fields output by NiftyReg (via brainreg) as a look up.
        """
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
                f"{len(points_out_of_bounds)} "
                f"points fell outside the atlas space",
            )

    def get_downsampled_space(self) -> AnatomicalSpace:
        """
        Get the anatomical space (as defined by brainglobe-space)
        for the downsampled data.

        Returns
        -------
        AnatomicalSpace
            The downsampled anatomical space (as defined by brainglobe-space).
        """
        target_shape = tifffile.imread(self.paths.downsampled_image).shape

        downsampled_space = AnatomicalSpace(
            self.atlas.orientation,
            shape=target_shape,
            resolution=self.atlas.resolution,
        )
        return downsampled_space

    def get_raw_data_space(self) -> AnatomicalSpace:
        """
        Get the anatomical space (as defined by brainglobe-space)
        for the raw data.

        Returns
        -------
        AnatomicalSpace
            The raw data anatomical space (as defined by brainglobe-space).
        """
        raw_data_space = AnatomicalSpace(
            self.metadata.orientation,
            shape=self.raw_data.data.shape,
            resolution=[float(i) for i in self.metadata.voxel_sizes],
        )
        return raw_data_space

    def analyse_points(self) -> None:
        """
        Analyse the distribution of points in the space
        of the BrainGlobe Atlas.
        """
        self.all_points_df, self.points_per_region_df = (
            summarise_points_by_atlas_region(
                self.points_layer.data,
                self.points_in_atlas_space,
                self.atlas,
                self.paths.volume_csv_path,
            )
        )

        self.populate_summary_table()
        self.brainrender_export_button.setVisible(True)
        self.save_all_points_button.setVisible(True)
        self.save_points_summary_button.setVisible(True)

        print("Analysing points")

    def populate_summary_table(
        self,
        columns_to_keep: List[str] = [
            "structure_name",
            "left_cell_count",
            "right_cell_count",
        ],
    ) -> None:
        """
        Populate the table with the summary of points per atlas region.

        Parameters
        ----------
        columns_to_keep : List[str], optional
            Columns to keep in the summary table.
            Default columns are ["structure_name", "left_cell_count",
            "right_cell_count"].
        """
        summary_df = self.points_per_region_df[columns_to_keep]
        self.points_per_region_table_model = DataFrameModel(summary_df)
        self.points_per_region_table.setModel(
            self.points_per_region_table_model
        )
        self.points_per_region_table_title.setVisible(True)
        self.points_per_region_table.setVisible(True)

    def export_points_to_brainrender(self) -> None:
        """
        Export points in the format required for brainrender
        N.B. assumes atlas is isotropic
        """
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Choose filename",
            "",
            "NumPy Files (*.npy)",
        )

        if path:
            path = ensure_extension(path, ".npy")
        export_points_to_brainrender(
            self.points_in_atlas_space, self.atlas.resolution[0], path
        )

    def save_all_points_csv(self) -> None:
        """
        Save the coordinate and atlas region
        information for all points to a CSV file.
        """
        self.save_df_to_csv(self.all_points_df)

    def save_points_summary_csv(self) -> None:
        """
        Save the summary of the distribution of points
        in the atlas space to a CSV file.
        """
        self.save_df_to_csv(self.points_per_region_df)

    def save_df_to_csv(self, df: pd.DataFrame) -> None:
        """
        Save the given DataFrame to a CSV file.

        Prompts the user to choose a filename and ensures the file has a
        .csv extension.
        The DataFrame is then saved to the specified file.

        Parameters
        ----------
        df : pd.DataFrame
            The DataFrame to be saved.

        Returns
        -------
        None
        """
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Choose filename",
            "",
            "CSV Files (*.csv)",
        )

        if path:
            path = ensure_extension(path, ".csv")
            df.to_csv(path, index=False)

    @staticmethod
    def is_atlas_installed(atlas: str) -> bool:
        """
        Check if the specified BrainGlobe atlas is installed.

        Parameters
        ----------
        atlas : str
            The atlas name to check.

        Returns
        -------
        bool
            True if the atlas is installed, False otherwise.
        """
        downloaded_atlases = get_downloaded_atlases()
        if atlas in downloaded_atlases:
            return True
        else:
            return False


class Paths:
    """
    A class to hold all brainreg-related file paths.

    N.B. this could be imported from brainreg, but it is copied here to
    prevent a circular dependency

    Attributes
    ----------
    brainreg_directory : Path
        Path to brainreg output directory (or brainmapper
        "registration" directory)
    brainreg_metadata_file : Path
        The path to the brainreg metadata (brainreg.json) file
    deformation_field_0 : Path
        The path to the deformation field (0th dimension)
    deformation_field_1 : Path
        The path to the deformation field (1st dimension)
    deformation_field_2 : Path
        The path to the deformation field (2nd dimension)
    downsampled_image : Path
        The path to the downsampled.tiff image file
    volume_csv_path : Path
        The path to the csv file containing region volumes

    Parameters
    ----------
    brainreg_directory : Union[str, Path]
        Path to brainreg output directory (or brainmapper
        "registration" directory)
    """

    def __init__(self, brainreg_directory: Union[str, Path]) -> None:
        """
        Set the paths based on the given brainreg directory

        Parameters
        ----------
        brainreg_directory : Union[str, Path]
            Path to brainreg output directory
            (or brainmapper "registration" directory).
        """
        self.brainreg_directory: Path = Path(brainreg_directory)
        self.brainreg_metadata_file: Path = self.make_filepaths(
            "brainreg.json"
        )
        self.deformation_field_0: Path = self.make_filepaths(
            "deformation_field_0.tiff"
        )
        self.deformation_field_1: Path = self.make_filepaths(
            "deformation_field_1.tiff"
        )
        self.deformation_field_2: Path = self.make_filepaths(
            "deformation_field_2.tiff"
        )
        self.downsampled_image: Path = self.make_filepaths("downsampled.tiff")
        self.volume_csv_path: Path = self.make_filepaths("volumes.csv")

    def make_filepaths(self, filename: str) -> Path:
        """
        Create a full file path by combining the directory with a filename.

        Parameters
        ----------
        filename : str
            The name of the file to create a path for.

        Returns
        -------
        Path
            The full path to the specified file.
        """
        return self.brainreg_directory / filename


class Metadata:
    """
    A class to represent brainreg registration metadata
    (loaded from brainreg.json)

    Attributes
    ----------
    orientation : str
        The orientation of the input data (in brainglobe-space format)
    atlas_string : str
        The BrainGlobe atlas used for brain registration.
    voxel_sizes : List[float]
        The voxel sizes of the input data

    Parameters
    ----------
    brainreg_metadata : Dict[str, Any]
        A dictionary containing metadata information,
        loaded from brainreg.json
    """

    def __init__(self, brainreg_metadata: Dict[str, Any]) -> None:
        """
        Initialize the Metadata instance with brainreg metadata.

        Parameters
        ----------
        brainreg_metadata : Dict[str, Any]
            A dictionary containing metadata information from brainreg.json
        """
        self.orientation: str = brainreg_metadata["orientation"]
        self.atlas_string: str = brainreg_metadata["atlas"]
        self.voxel_sizes: List[float] = brainreg_metadata["voxel_sizes"]
