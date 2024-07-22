from pathlib import Path
from typing import Any, Dict

import numpy as np
import pooch
import pytest

from brainglobe_utils.brainmapper.transform_widget import Metadata, Paths, TransformPoints

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
def transformation_widget_with_napari_layers(
    make_napari_viewer, brainreg_directory
):
    viewer = make_napari_viewer()
    widget = TransformPoints(viewer)
    viewer.window.add_dock_widget(widget)
    points_layer = viewer.add_points(points)
    widget.points_layer = points_layer

    raw_data = brainreg_directory / "downsampled.tiff"
    raw_data_layer = viewer.open(raw_data)
    widget.raw_data = raw_data_layer[0]
    return widget


@pytest.fixture
def brainreg_directory() -> Path:
    download_path = Path.home() / ".brainglobe" / "test_data"
    _ = pooch.retrieve(
        url="https://gin.g-node.org/BrainGlobe/test-data/raw/master/"
        "brainglobe-utils/points_transform_brainreg_directory.zip",
        known_hash="a1997f61a5efa752584ea91b7c479506343215bb91f5be09a72349f24e21fc54",
        path=download_path,
        progressbar=True,
        processor=pooch.Unzip(extract_dir="../test_brainreg"),
    )
    return download_path / "points_transform_brainreg_directory"


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
