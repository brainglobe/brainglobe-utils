from pathlib import Path
from typing import Any, Dict

import pytest

from brainglobe_utils.brainreg.napari import Metadata, Paths


@pytest.fixture
def brainreg_directory() -> Path:
    return Path("/path/to/brainreg_directory")


@pytest.fixture
def paths(brainreg_directory) -> Paths:
    return Paths(brainreg_directory)


def test_paths_initialization(paths, brainreg_directory):
    assert paths.brainreg_directory == brainreg_directory
    assert paths.brainreg_metadata_file == brainreg_directory / "brainreg.json"
    assert (
        paths.deformation_field_0
        == brainreg_directory / "deformation_field_0.tiff"
    )
    assert paths.downsampled_image == brainreg_directory / "downsampled.tiff"
    assert paths.volume_csv_path == brainreg_directory / "volumes.csv"


def test_make_filepaths(paths, brainreg_directory):
    filename = "test_file.txt"
    expected_path = brainreg_directory / filename
    assert paths.make_filepaths(filename) == expected_path


@pytest.fixture
def sample_metadata() -> Dict[str, Any]:
    return {
        "orientation": "prs",
        "atlas": "allen_mouse_25um",
        "voxel_sizes": [5, 2, 2],
    }


def test_metadata_initialization(sample_metadata):
    metadata = Metadata(sample_metadata)
    assert metadata.orientation == sample_metadata["orientation"]
    assert metadata.atlas_string == sample_metadata["atlas"]
    assert metadata.voxel_sizes == sample_metadata["voxel_sizes"]
