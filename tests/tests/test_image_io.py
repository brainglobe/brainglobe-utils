import numpy as np
import pytest
from tifffile import tifffile

from brainglobe_utils.image_io import load, save, utils


@pytest.fixture()
def layer():
    """Create a 4x4 array of 32-bit integers"""
    return np.tile(np.array([1, 2, 3, 4], dtype=np.int32), (4, 1))


@pytest.fixture()
def start_array(layer):
    """Create a 4x4x4 array of 32-bit integers"""
    volume = np.dstack((layer, 2 * layer, 3 * layer, 4 * layer))
    return volume


def test_tiff_io(tmp_path, layer):
    """
    Test that a 2D tiff can be written and read correctly with tifffile
    """
    dest_path = tmp_path / "layer.tiff"
    tifffile.imwrite(dest_path, layer)
    reloaded = tifffile.imread(dest_path)
    assert (reloaded == layer).all()


def test_to_tiffs(tmp_path, start_array):
    """
    Test that a 3D image can be written and read correctly as a sequence
    of 2D tiffs
    """
    save.to_tiffs(start_array, str(tmp_path / "start_array"))
    reloaded_array = load.load_from_folder(str(tmp_path), 1, 1, 1)
    assert (reloaded_array == start_array).all()


def test_load_img_sequence(tmp_path, start_array):
    """
    Test that a tiff sequence can be loaded from a text file containing an
    ordered list of the tiff file paths (one per line)
    """
    # Write tiff sequence to sub-folder
    folder = tmp_path / "sub"
    folder.mkdir()
    save.to_tiffs(start_array, str(folder / "start_array"))

    # Write txt file containing all tiff file paths (one per line)
    img_sequence_file = tmp_path / "imgs_file.txt"
    img_sequence_file.write_text(
        "\n".join([str(folder / fname) for fname in sorted(folder.iterdir())])
    )

    # Load image from paths in text file
    reloaded_array = load.load_img_sequence(str(img_sequence_file), 1, 1, 1)
    assert (reloaded_array == start_array).all()


def test_to_nii(tmp_path, start_array):
    """
    Test that a 3D image can be written and read correctly as nii
    """
    nii_path = str(tmp_path / "test_array.nii")
    save.to_nii(start_array, nii_path)
    assert (load.load_nii(nii_path).get_fdata() == start_array).all()


def test_scale_z(start_array):
    """
    Test that a 3D image can be scaled in z by float and integer values
    """
    assert utils.scale_z(start_array, 0.5).shape[0] == start_array.shape[0] / 2
    assert utils.scale_z(start_array, 2).shape[0] == start_array.shape[0] * 2
