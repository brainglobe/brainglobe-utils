import json
from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd
import pooch
import pytest
from brainglobe_atlasapi import BrainGlobeAtlas

from brainglobe_utils.brainmapper.transform_widget import (
    Metadata,
    Paths,
    TransformPoints,
)

RAW_DATA_ORIENTATION = ATLAS_ORIENTATION = "asr"
points = np.array(
    [
        [10, 68, 105],
        [10, 90, 134],
        [10, 105, 157],
        [36, 69, 86],
        [36, 72, 155],
        [36, 112, 128],
        [74, 54, 60],
        [74, 121, 50],
        [74, 87, 153],
        [74, 84, 169],
        [74, 108, 156],
        [74, 75, 148],
        [74, 98, 169],
        [74, 76, 159],
        [74, 99, 156],
        [74, 91, 146],
        [74, 87, 160],
        [112, 44, 60],
        [112, 76, 136],
        [156, 77, 54],
        [173, 126, 159],
        [201, 66, 130],
        [219, 132, 199],
        [219, 1, 1],
    ]
)

points_outside_brain = np.array(
    [
        [10000, 10000, 10000],
        [100001, 100001, 100001],
    ]
)


points_in_downsampled_space = np.array(
    [
        [10.0, 68.0, 105.0],
        [10.0, 90.0, 134.0],
        [10.0, 105.0, 157.0],
        [36.0, 69.0, 86.0],
        [36.0, 72.0, 155.0],
        [36.0, 112.0, 128.0],
        [74.0, 54.0, 60.0],
        [74.0, 121.0, 50.0],
        [74.0, 87.0, 153.0],
        [74.0, 84.0, 169.0],
        [74.0, 108.0, 156.0],
        [74.0, 75.0, 148.0],
        [74.0, 98.0, 169.0],
        [74.0, 76.0, 159.0],
        [74.0, 99.0, 156.0],
        [74.0, 91.0, 146.0],
        [74.0, 87.0, 160.0],
        [112.0, 44.0, 60.0],
        [112.0, 76.0, 136.0],
        [156.0, 77.0, 54.0],
        [173.0, 126.0, 159.0],
        [201.0, 66.0, 130.0],
        [219.0, 132.0, 199.0],
        [219.0, 1.0, 1.0],
    ]
)

points_in_atlas_space = np.array(
    [
        [36, 54, 97],
        [34, 76, 124],
        [34, 90, 146],
        [61, 58, 82],
        [62, 60, 145],
        [58, 101, 120],
        [100, 47, 60],
        [93, 113, 53],
        [95, 80, 146],
        [95, 76, 161],
        [93, 100, 148],
        [97, 67, 141],
        [94, 90, 161],
        [97, 68, 151],
        [94, 92, 148],
        [95, 84, 139],
        [95, 80, 152],
        [139, 42, 60],
        [131, 72, 132],
        [173, 81, 56],
        [177, 135, 155],
        [214, 79, 129],
        [218, 150, 194],
        [249, 17, 10],
    ]
)


@pytest.fixture
def sample_dataframe():
    return pd.DataFrame({"column1": [1, 2, 3], "column2": ["a", "b", "c"]})


@pytest.fixture
def random_json_path(tmp_path):
    json_path = tmp_path / "random_json.json"
    content = {
        "name": "Pooh Bear",
        "location": "100 acre wood",
        "food": "Honey",
    }
    with open(json_path, "w") as f:
        json.dump(content, f)

    return json_path


@pytest.fixture
def mock_display_info(mocker):
    return mocker.patch(
        "brainglobe_utils.brainmapper.transform_widget.display_info"
    )


@pytest.fixture(scope="function")
def transformation_widget_with_transformed_points(
    transformation_widget_with_data,
):
    transformation_widget_with_data.run_transform_points_to_downsampled_space()
    transformation_widget_with_data.run_transform_downsampled_points_to_atlas_space()
    return transformation_widget_with_data


@pytest.fixture(scope="function")
def transformation_widget_with_data(
    transformation_widget_with_napari_layers, brainreg_directory
):
    transformation_widget_with_napari_layers.brainreg_directory = (
        brainreg_directory
    )
    transformation_widget_with_napari_layers.initialise_brainreg_data()
    return transformation_widget_with_napari_layers


@pytest.fixture(scope="function")
def transformation_widget(make_napari_viewer):
    viewer = make_napari_viewer()
    widget = TransformPoints(viewer)
    viewer.window.add_dock_widget(widget)
    return widget


@pytest.fixture(scope="function")
def transformation_widget_with_napari_layers(
    transformation_widget, brainreg_directory
):
    points_layer = transformation_widget.viewer.add_points(points)
    transformation_widget.points_layer = points_layer

    raw_data = brainreg_directory / "downsampled.tiff"
    raw_data_layer = transformation_widget.viewer.open(raw_data)
    transformation_widget.raw_data = raw_data_layer[0]
    return transformation_widget


@pytest.fixture
def brainreg_directory(test_data_registry) -> Path:
    _ = test_data_registry.fetch(
        "brainglobe-utils/points_transform_brainreg_directory.zip",
        progressbar=True,
        processor=pooch.Unzip(extract_dir=""),
    )
    return (
        Path.home()
        / ".brainglobe"
        / "test_data"
        / "brainglobe-utils"
        / "points_transform_brainreg_directory"
    )


def test_download_brainreg_directory(brainreg_directory):
    assert brainreg_directory.exists()


def test_atlas_download():
    atlas_name = "allen_mouse_50um"
    atlas = BrainGlobeAtlas(atlas_name)
    assert atlas.atlas_name == atlas_name


@pytest.fixture
def dummy_brainreg_directory() -> Path:
    return Path("/path/to/brainreg_directory")


@pytest.fixture
def dummy_brainreg_file_paths(dummy_brainreg_directory) -> Paths:
    return Paths(dummy_brainreg_directory)


def test_initialise_brainreg_data(
    transformation_widget_with_data, brainreg_directory
):

    assert (
        transformation_widget_with_data.paths.brainreg_directory
        == brainreg_directory
    )
    assert (
        transformation_widget_with_data.metadata.orientation
        == ATLAS_ORIENTATION
    )
    assert (
        transformation_widget_with_data.atlas.atlas_name == "allen_mouse_50um"
    )


def test_get_downsampled_space(transformation_widget_with_data):
    downsampled_space = transformation_widget_with_data.get_downsampled_space()
    assert downsampled_space.origin_string == ATLAS_ORIENTATION


def test_get_raw_data_space(transformation_widget_with_data):
    raw_data_space = transformation_widget_with_data.get_raw_data_space()
    assert raw_data_space.origin_string == RAW_DATA_ORIENTATION


def test_call_transform_points_to_atlas_space(
    mocker, transformation_widget_with_data
):
    mock_load_brainreg = mocker.patch.object(
        transformation_widget_with_data, "load_brainreg_directory"
    )
    mock_transform_downsampled = mocker.patch.object(
        transformation_widget_with_data,
        "run_transform_points_to_downsampled_space",
    )
    mock_transform_atlas = mocker.patch.object(
        transformation_widget_with_data,
        "run_transform_downsampled_points_to_atlas_space",
    )
    mock_analyse_points = mocker.patch.object(
        transformation_widget_with_data, "analyse_points"
    )

    transformation_widget_with_data.transform_points_to_atlas_space()
    mock_load_brainreg.assert_called_once()
    mock_transform_downsampled.assert_called_once()
    mock_transform_atlas.assert_called_once()
    mock_analyse_points.assert_called_once()


def test_transform_points_to_atlas_space(
    transformation_widget_with_transformed_points,
):
    np.testing.assert_array_equal(
        transformation_widget_with_transformed_points.viewer.layers[
            "Points in downsampled space"
        ].data,
        points_in_downsampled_space,
    )
    np.testing.assert_array_equal(
        transformation_widget_with_transformed_points.viewer.layers[
            "Points in atlas space"
        ].data,
        points_in_atlas_space,
    )


def test_transformation_raises_info_points_out_of_bounds(
    transformation_widget_with_data, mock_display_info
):
    points_layer = transformation_widget_with_data.viewer.add_points(
        points_outside_brain
    )
    transformation_widget_with_data.points_layer = points_layer
    transformation_widget_with_data.run_transform_points_to_downsampled_space()
    transformation_widget_with_data.run_transform_downsampled_points_to_atlas_space()
    mock_display_info.assert_called_once_with(
        transformation_widget_with_data,
        "Points outside atlas",
        "2 points fell outside the atlas space",
    )


def test_check_layers(transformation_widget_with_data):
    assert transformation_widget_with_data.check_layers()


def test_check_layers_no_layers(transformation_widget, mock_display_info):
    transformation_widget.check_layers()

    mock_display_info.assert_called_once_with(
        transformation_widget,
        "No layers selected",
        "Please select the layers corresponding to the points "
        "you would like to transform and the raw data (registered by "
        "brainreg)",
    )


def test_check_layers_no_raw_data(transformation_widget, mock_display_info):
    points_layer = transformation_widget.viewer.add_points(points)
    transformation_widget.points_layer = points_layer

    transformation_widget.check_layers()

    mock_display_info.assert_called_once_with(
        transformation_widget,
        "No raw data layer selected",
        "Please select a layer that corresponds to the raw "
        "data (registered by brainreg)",
    )


def test_check_layers_no_points_data(
    transformation_widget, brainreg_directory, mock_display_info
):
    raw_data = brainreg_directory / "downsampled.tiff"
    raw_data_layer = transformation_widget.viewer.open(raw_data)
    transformation_widget.raw_data = raw_data_layer[0]

    transformation_widget.check_layers()

    mock_display_info.assert_called_once_with(
        transformation_widget,
        "No points layer selected",
        "Please select a points layer you would like to transform",
    )


def test_load_brainreg_directory(
    transformation_widget_with_napari_layers, brainreg_directory, mocker
):
    # Mock dialog to avoid need for UI
    mock_get_save_file_name = mocker.patch(
        "brainglobe_utils.brainmapper.transform_widget.QFileDialog.getExistingDirectory"
    )
    mock_get_save_file_name.return_value = brainreg_directory

    transformation_widget_with_napari_layers.load_brainreg_directory()
    assert (
        transformation_widget_with_napari_layers.atlas.atlas_name
        == "allen_mouse_50um"
    )


def test_load_brainreg_directory_no_input(
    transformation_widget_with_napari_layers, mocker
):
    # Mock dialog to avoid need for UI
    mock_get_save_file_name = mocker.patch(
        "brainglobe_utils.brainmapper.transform_widget.QFileDialog.getExistingDirectory"
    )
    mock_get_save_file_name.return_value = ""

    transformation_widget_with_napari_layers.load_brainreg_directory()
    assert not hasattr(
        transformation_widget_with_napari_layers.atlas, "atlas_name"
    )


def test_check_brainreg_directory_correct_metadata(
    mocker, transformation_widget_with_data
):
    mock_method = mocker.patch.object(
        transformation_widget_with_data, "display_brainreg_directory_warning"
    )

    transformation_widget_with_data.check_brainreg_directory()
    mock_method.assert_not_called()


def test_check_brainreg_directory_random_data(
    mocker, transformation_widget_with_data, random_json_path
):
    mock_method = mocker.patch.object(
        transformation_widget_with_data, "display_brainreg_directory_warning"
    )
    transformation_widget_with_data.paths.brainreg_metadata_file = (
        random_json_path
    )
    transformation_widget_with_data.check_brainreg_directory()
    mock_method.assert_called_once()


def test_check_brainreg_directory_false_path(
    mocker, transformation_widget_with_data
):
    mock_method = mocker.patch.object(
        transformation_widget_with_data, "display_brainreg_directory_warning"
    )

    transformation_widget_with_data.paths.brainreg_metadata_file = "/some/file"
    transformation_widget_with_data.check_brainreg_directory()
    mock_method.assert_called_once()


def test_display_brainreg_directory_warning_calls_display_info(
    transformation_widget_with_napari_layers, mock_display_info
):
    transformation_widget_with_napari_layers.display_brainreg_directory_warning()

    # Assert display_info was called once with the expected arguments
    mock_display_info.assert_called_once_with(
        transformation_widget_with_napari_layers,
        "Not a brainreg directory",
        "This directory does not appear to be a valid brainreg directory. "
        "Please try loading another brainreg output directory.",
    )


def test_warn_user_about_atlas_download(
    transformation_widget_with_data, mocker, mock_display_info
):
    mock_is_atlas_installed = mocker.patch(
        "brainglobe_utils.brainmapper.transform_widget.TransformPoints.is_atlas_installed"
    )
    mock_is_atlas_installed.return_value = False

    transformation_widget_with_data.load_atlas()
    mock_display_info.assert_called_once_with(
        transformation_widget_with_data,
        "Atlas not downloaded",
        "Atlas: allen_mouse_50um needs to be "
        "downloaded. This may take some time depending on "
        "the size of the atlas and your network speed.",
    )


def test_layers_not_in_place_return(mocker, transformation_widget):
    mock_is_atlas_installed = mocker.patch(
        "brainglobe_utils.brainmapper.transform_widget.TransformPoints.check_layers"
    )
    mock_is_atlas_installed.return_value = False
    assert transformation_widget.transform_points_to_atlas_space() is None


def test_transform_points_return_if_no_brainreg(
    mocker, transformation_widget_with_data
):
    mock_is_atlas_installed = mocker.patch(
        "brainglobe_utils.brainmapper.transform_widget.TransformPoints.load_brainreg_directory"
    )
    mock_is_atlas_installed.return_value = False
    assert (
        transformation_widget_with_data.transform_points_to_atlas_space()
        is None
    )


def test_analysis(transformation_widget_with_transformed_points):
    transformation_widget_with_transformed_points.analyse_points()

    assert (
        transformation_widget_with_transformed_points.all_points_df.shape[0]
        == 21
    )

    df = transformation_widget_with_transformed_points.points_per_region_df
    assert (
        df.loc[
            df["structure_name"] == "Caudoputamen", "left_cell_count"
        ].values[0]
        == 9
    )
    assert (
        df.loc[df["structure_name"] == "Pons", "left_cell_count"].values[0]
        == 1
    )
    assert (
        df.loc[
            df["structure_name"]
            == "Primary somatosensory area, upper limb, layer 5",
            "left_cells_per_mm3",
        ].values[0]
        == 0
    )


def test_save_df_to_csv(
    mocker,
    transformation_widget_with_transformed_points,
    sample_dataframe,
    tmp_path,
):
    # Mock dialog to avoid need for UI
    mock_get_save_file_name = mocker.patch(
        "brainglobe_utils.brainmapper.transform_widget.QFileDialog.getSaveFileName"
    )

    save_path = tmp_path / "test.csv"
    mock_get_save_file_name.return_value = (save_path, "CSV Files (*.csv)")

    transformation_widget_with_transformed_points.save_df_to_csv(
        sample_dataframe
    )

    # Ensure the file dialog was called
    mock_get_save_file_name.assert_called_once_with(
        transformation_widget_with_transformed_points,
        "Choose filename",
        "",
        "CSV Files (*.csv)",
    )

    assert save_path.exists()


def test_save_all_points_and_summary_csv(
    mocker,
    transformation_widget_with_transformed_points,
    tmp_path,
):
    transformation_widget_with_transformed_points.analyse_points()

    # Mock dialog to avoid need for UI
    mock_get_save_file_name = mocker.patch(
        "brainglobe_utils.brainmapper.transform_widget.QFileDialog.getSaveFileName"
    )

    save_path = tmp_path / "all_points.csv"
    mock_get_save_file_name.return_value = (save_path, "CSV Files (*.csv)")
    transformation_widget_with_transformed_points.save_all_points_csv()
    assert save_path.exists()

    save_path = tmp_path / "points_per_region.csv"
    mock_get_save_file_name.return_value = (save_path, "CSV Files (*.csv)")
    transformation_widget_with_transformed_points.save_points_summary_csv()
    assert save_path.exists()


def test_is_atlas_installed(mocker, transformation_widget):
    mock_get_downloaded_atlases = mocker.patch(
        "brainglobe_utils.brainmapper.transform_widget.get_downloaded_atlases"
    )
    mock_get_downloaded_atlases.return_value = [
        "allen_mouse_10um",
        "allen_mouse_50um",
    ]

    assert transformation_widget.is_atlas_installed("allen_mouse_10um")
    assert not transformation_widget.is_atlas_installed("allen_mouse_25um")


def test_paths_initialisation(
    dummy_brainreg_file_paths, dummy_brainreg_directory
):
    assert (
        dummy_brainreg_file_paths.brainreg_directory
        == dummy_brainreg_directory
    )
    assert (
        dummy_brainreg_file_paths.brainreg_metadata_file
        == dummy_brainreg_directory / "brainreg.json"
    )
    assert (
        dummy_brainreg_file_paths.deformation_field_0
        == dummy_brainreg_directory / "deformation_field_0.tiff"
    )
    assert (
        dummy_brainreg_file_paths.downsampled_image
        == dummy_brainreg_directory / "downsampled.tiff"
    )
    assert (
        dummy_brainreg_file_paths.volume_csv_path
        == dummy_brainreg_directory / "volumes.csv"
    )


def test_make_filepaths(dummy_brainreg_file_paths, dummy_brainreg_directory):
    filename = "test_file.txt"
    expected_path = dummy_brainreg_directory / filename
    assert dummy_brainreg_file_paths.make_filepaths(filename) == expected_path


@pytest.fixture
def sample_metadata() -> Dict[str, Any]:
    return {
        "orientation": "prs",
        "atlas": "allen_mouse_25um",
        "voxel_sizes": [5, 2, 2],
    }


def test_metadata_initialisation(sample_metadata):
    metadata = Metadata(sample_metadata)
    assert metadata.orientation == sample_metadata["orientation"]
    assert metadata.atlas_string == sample_metadata["atlas"]
    assert metadata.voxel_sizes == sample_metadata["voxel_sizes"]
