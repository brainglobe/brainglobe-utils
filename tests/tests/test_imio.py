import os
import pytest

import numpy as np

from tifffile import tifffile

from imio import load, save, utils


@pytest.fixture()
def layer():
    return np.tile(np.array([1, 2, 3, 4]), (4, 1))


@pytest.fixture()
def start_array(layer):
    volume = np.dstack((layer, 2 * layer, 3 * layer, 4 * layer))
    return volume


def test_tiff_io(tmpdir, layer):
    folder = str(tmpdir)
    dest_path = os.path.join(folder, "layer.tiff")
    tifffile.imsave(dest_path, layer)
    reloaded = tifffile.imread(dest_path)
    assert (reloaded == layer).all()


def test_to_tiffs(tmpdir, start_array):
    folder = str(tmpdir)
    save.to_tiffs(start_array, os.path.join(folder, "start_array"))
    reloaded_array = load.load_from_folder(folder, 1, 1, 1)
    assert (reloaded_array == start_array).all()


def test_load_img_sequence(tmpdir, start_array):
    folder = str(tmpdir.mkdir("sub"))
    save.to_tiffs(start_array, os.path.join(folder, "start_array"))
    img_sequence_file = tmpdir.join("imgs_file.txt")
    img_sequence_file.write(
        "\n".join(
            [
                os.path.join(folder, fname)
                for fname in sorted(os.listdir(folder))
            ]
        )
    )
    reloaded_array = load.load_img_sequence(str(img_sequence_file), 1, 1, 1)
    assert (reloaded_array == start_array).all()


def test_to_nii(tmpdir, start_array):  # Also tests load_nii
    folder = str(tmpdir)
    nii_path = os.path.join(folder, "test_array.nii")
    save.to_nii(start_array, nii_path)
    assert (load.load_nii(nii_path).get_data() == start_array).all()


def test_scale_z(start_array):
    assert (
        utils.scale_z(start_array, 0.5).shape[-1] == start_array.shape[-1] / 2
    )
    assert utils.scale_z(start_array, 2).shape[-1] == start_array.shape[-1] * 2
