import random
from collections import namedtuple
from unittest import mock

import numpy as np
import psutil
import pytest
import tifffile

from brainglobe_utils.IO.image import load, save, utils


@pytest.fixture()
def array_2d():
    """Create a 4x4 array of 32-bit integers"""
    return np.tile(np.array([1, 2, 3, 4], dtype=np.int32), (4, 1))


@pytest.fixture()
def array_3d(array_2d):
    """Create a 4x4x4 array of 32-bit integers"""
    volume = np.stack((array_2d, 2 * array_2d, 3 * array_2d, 4 * array_2d))
    return volume


@pytest.fixture()
def array_3D_as_2d_tiffs_path(tmp_path, array_3d, prefix="image"):
    dest_path = tmp_path / prefix
    save.to_tiffs(array_3d, dest_path)
    return tmp_path


@pytest.fixture()
def txt_path(tmp_path, array_3d):
    """
    Return the path to a text file containing the paths of a series of 2D tiffs
    in order
    """
    txt_path = tmp_path / "imgs_file.txt"
    directory = txt_path.parent

    # Write tiff sequence to sub-folder
    sub_dir = directory / "sub"
    sub_dir.mkdir()
    save.to_tiffs(array_3d, sub_dir / "image")

    # Write txt file containing all tiff file paths (one per line)
    tiff_paths = sorted(sub_dir.iterdir())
    txt_path.write_text(
        "\n".join([str(sub_dir / fname) for fname in tiff_paths])
    )

    return txt_path


@pytest.fixture()
def shuffled_txt_path(txt_path):
    """
    Return the path to a text file containing the paths of a series of 2D tiffs
    in a random order
    """
    # Shuffle paths in the text file into a random order
    with open(txt_path, "r+") as f:
        tiff_paths = f.read().splitlines()
        random.Random(4).shuffle(tiff_paths)
        f.seek(0)
        f.writelines(line + "\n" for line in tiff_paths)
        f.truncate()

    return txt_path


@pytest.fixture
def array3d_as_tiff_stack_with_missing_metadata(array_3d, tmp_path):
    tiff_path = tmp_path / "test_missing_metadata.tif"
    metadata = {"axes": ""}
    tifffile.imwrite(
        tiff_path, array_3d, photometric="minisblack", metadata=metadata
    )
    return tiff_path


@pytest.mark.parametrize("use_path", [True, False], ids=["Path", "String"])
def test_tiff_io(tmp_path, array_3d, use_path):
    """
    Test that a 3D tiff can be written and read correctly, using string
    or pathlib.Path input.
    """
    filename = "image_array.tiff"
    if use_path:
        dest_path = tmp_path / filename
    else:
        dest_path = str(tmp_path / filename)

    save.to_tiff(array_3d, dest_path)
    reloaded = load.load_img_stack(dest_path, 1, 1, 1)

    np.testing.assert_array_equal(reloaded, array_3d)


@pytest.mark.parametrize(
    "x_scaling_factor, y_scaling_factor, z_scaling_factor",
    [(1, 1, 1), (0.5, 0.5, 1), (0.25, 0.25, 0.25)],
)
def test_3d_tiff_scaling(
    tmp_path, array_3d, x_scaling_factor, y_scaling_factor, z_scaling_factor
):
    """
    Test that a 3D tiff is scaled correctly on loading
    """
    dest_path = tmp_path / "image_array.tiff"
    save.save_any(array_3d, dest_path)
    reloaded = load.load_any(
        dest_path,
        x_scaling_factor=x_scaling_factor,
        y_scaling_factor=y_scaling_factor,
        z_scaling_factor=z_scaling_factor,
    )

    assert reloaded.shape[0] == array_3d.shape[0] * z_scaling_factor
    assert reloaded.shape[1] == array_3d.shape[1] * y_scaling_factor
    assert reloaded.shape[2] == array_3d.shape[2] * x_scaling_factor


@pytest.mark.parametrize("use_str", [True, False], ids=["String", "Path"])
@pytest.mark.parametrize(
    "load_parallel",
    [
        pytest.param(True, id="parallel loading"),
        pytest.param(False, id="no parallel loading"),
    ],
)
def test_tiff_sequence_io(
    array_3d, array_3D_as_2d_tiffs_path, load_parallel, use_str
):
    """
    Test that a 3D image can be written and read correctly as a sequence
    of 2D tiffs (with or without parallel loading). Tests using both
    string and pathlib.Path input.
    """
    dir_path = array_3D_as_2d_tiffs_path
    if use_str:
        dir_path = str(dir_path)

    reloaded_array = load.load_from_folder(
        dir_path, load_parallel=load_parallel
    )
    np.testing.assert_array_equal(reloaded_array, array_3d)


def test_2d_tiff(tmp_path, array_2d):
    """
    Test that an error is thrown when loading a single 2D tiff
    """
    image_path = tmp_path / "image.tif"
    save.to_tiff(array_2d, image_path)

    with pytest.raises(utils.ImageIOLoadException):
        load.load_any(image_path)


@pytest.mark.parametrize(
    "x_scaling_factor, y_scaling_factor, z_scaling_factor",
    [(1, 1, 1), (0.5, 0.5, 1), (0.25, 0.25, 0.25)],
)
def test_tiff_sequence_scaling(
    tmp_path, array_3d, x_scaling_factor, y_scaling_factor, z_scaling_factor
):
    """
    Test that a tiff sequence is scaled correctly on loading
    """
    save.save_any(array_3d, tmp_path)
    reloaded_array = load.load_any(
        tmp_path,
        x_scaling_factor=x_scaling_factor,
        y_scaling_factor=y_scaling_factor,
        z_scaling_factor=z_scaling_factor,
    )

    assert reloaded_array.shape[0] == array_3d.shape[0] * z_scaling_factor
    assert reloaded_array.shape[1] == array_3d.shape[1] * y_scaling_factor
    assert reloaded_array.shape[2] == array_3d.shape[2] * x_scaling_factor


def test_tiff_sequence_one_tiff(tmp_path):
    """
    Test that an error is thrown when loading a directory containing a
    single tiff via load_any
    """
    save.to_tiff(np.ones((3, 3)), tmp_path / "image.tif")

    with pytest.raises(utils.ImageIOLoadException):
        load.load_any(tmp_path)


@pytest.mark.parametrize(
    "load_parallel",
    [
        pytest.param(True, id="parallel loading"),
        pytest.param(False, id="no parallel loading"),
    ],
)
def test_tiff_sequence_diff_shape(tmp_path, array_3d, load_parallel):
    """
    Test that an error is thrown when trying to load a tiff sequence where
    individual 2D tiffs have different shapes
    """
    save.to_tiff(np.ones((2, 2)), tmp_path / "image_1.tif")
    save.to_tiff(np.ones((3, 3)), tmp_path / "image_2.tif")

    with pytest.raises(utils.ImageIOLoadException):
        load.load_any(tmp_path, load_parallel=load_parallel)


@pytest.mark.parametrize("use_path", [True, False], ids=["Path", "String"])
def test_load_img_sequence_from_txt(txt_path, array_3d, use_path):
    """
    Test that a tiff sequence can be read from a text file containing an
    ordered list of the tiff file paths (one per line). Tests using both str
    and pathlib.Path input.
    """
    if not use_path:
        txt_path = str(txt_path)

    reloaded_array = load.load_img_sequence(txt_path)
    np.testing.assert_array_equal(reloaded_array, array_3d)


@pytest.mark.parametrize(
    "sort",
    [True, False],
)
def test_sort_img_sequence_from_txt(shuffled_txt_path, array_3d, sort):
    """
    Test that shuffled filepaths read from a txt file can be sorted correctly
    """
    # Load image from shuffled paths in text file
    reloaded_array = load.load_img_sequence(
        shuffled_txt_path, 1, 1, 1, sort=sort
    )
    if sort:
        np.testing.assert_array_equal(reloaded_array, array_3d)
    else:
        assert not np.array_equal(reloaded_array, array_3d)


@pytest.mark.parametrize("use_path", [True, False], ids=["Path", "String"])
def test_nii_io(tmp_path, array_3d, use_path):
    """
    Test that a 3D image can be written and read correctly as nii with scale
    (keeping it as a nifty object with no numpy conversion on loading).
    Tests using both str and pathlib.Path input.
    """
    filename = "test_array.nii"
    if use_path:
        nii_path = tmp_path / filename
    else:
        nii_path = str(tmp_path / filename)

    scale = (5, 5, 5)
    save.to_nii(array_3d, nii_path, scale=scale)
    reloaded = load.load_nii(nii_path)

    assert (reloaded.get_fdata() == array_3d).all()
    assert reloaded.header.get_zooms() == scale


def test_nii_read_to_numpy(tmp_path, array_3d):
    """
    Test that conversion of loaded nii image to an in-memory numpy array works
    """
    nii_path = tmp_path / "test_array.nii"
    save.save_any(array_3d, nii_path)
    reloaded_array = load.load_any(nii_path, as_numpy=True)

    np.testing.assert_array_equal(reloaded_array, array_3d)


@pytest.mark.parametrize("use_path", [True, False], ids=["Path", "String"])
def test_nrrd_io(tmp_path, array_3d, use_path):
    """
    Test that a 3D image can be written and read correctly as nrrd, using both
    str and pathlib.Path input.
    """
    filename = "test_array.nrrd"
    if use_path:
        nrrd_path = tmp_path / filename
    else:
        nrrd_path = str(tmp_path / filename)

    save.to_nrrd(array_3d, nrrd_path)
    assert (load.load_nrrd(nrrd_path) == array_3d).all()


@pytest.mark.parametrize("use_path", [True, False], ids=["Path", "String"])
@pytest.mark.parametrize(
    "file_name",
    [
        "test_array.tiff",
        "test_array.tif",
        "test_array.nrrd",
        "test_array.nii",
        pytest.param("", id="dir of tiffs"),
    ],
)
def test_save_and_load_any(tmp_path, array_3d, file_name, use_path):
    """
    Test that save_any/load_any can write/read all required image
    file types. Tests using both string and pathlib.Path input.
    """
    if use_path:
        src_path = tmp_path / file_name
    else:
        src_path = str(tmp_path / file_name)
    save.save_any(array_3d, src_path)

    assert (load.load_any(src_path) == array_3d).all()


@pytest.mark.parametrize("use_path", [True, False], ids=["Path", "String"])
def test_load_any_txt(txt_path, array_3d, use_path):
    """
    Test that load_any can read a tiff sequence from a text file containing an
    ordered list of the tiff file paths (one per line). Tests using both
    string and pathlib.Path input.
    """
    if not use_path:
        txt_path = str(txt_path)
    assert (load.load_any(txt_path) == array_3d).all()


def test_load_any_error(tmp_path):
    """
    Test that load_any throws an error for an unknown file extension
    """
    with pytest.raises(NotImplementedError):
        load.load_any(tmp_path / "test.unknown")


def test_save_any_error(tmp_path, array_3d):
    """
    Test that save_any throws an error for an unknown file extension
    """
    with pytest.raises(NotImplementedError):
        save.save_any(array_3d, tmp_path / "test.unknown")


def test_scale_z(array_3d):
    """
    Test that a 3D image can be scaled in z by float and integer values
    """
    assert utils.scale_z(array_3d, 0.5).shape[0] == array_3d.shape[0] / 2
    assert utils.scale_z(array_3d, 2).shape[0] == array_3d.shape[0] * 2


def test_image_size_dir(tmp_path, array_3d):
    """
    Test that image size can be detected from a directory of 2D tiffs
    """
    save.save_any(array_3d, tmp_path)

    image_shape = load.get_size_image_from_file_paths(tmp_path)
    assert image_shape["x"] == array_3d.shape[2]
    assert image_shape["y"] == array_3d.shape[1]
    assert image_shape["z"] == array_3d.shape[0]


def test_image_size_tiff_stack(tmp_path, array_3d):
    """
    Test that image size can be detected from a directory of 2D tiffs
    """
    filename = tmp_path.joinpath("image_size_tiff_stack.tif")
    save.save_any(array_3d, filename)

    image_shape = load.get_size_image_from_file_paths(filename)
    assert image_shape["x"] == array_3d.shape[2]
    assert image_shape["y"] == array_3d.shape[1]
    assert image_shape["z"] == array_3d.shape[0]


def test_image_size_txt(txt_path, array_3d):
    """
    Test that image size can be detected from a text file containing the paths
    of a sequence of 2D tiffs
    """
    image_shape = load.get_size_image_from_file_paths(txt_path)
    assert image_shape["x"] == array_3d.shape[2]
    assert image_shape["y"] == array_3d.shape[1]
    assert image_shape["z"] == array_3d.shape[0]


def test_memory_error(monkeypatch):
    """
    Test that check_mem throws an error when there's not enough memory
    available.
    """

    # Use monkeypatch to always return a set value for the available memory.
    def mock_memory():
        VirtualMemory = namedtuple("VirtualMemory", "available")
        return VirtualMemory(500)

    monkeypatch.setattr(psutil, "virtual_memory", mock_memory)

    with pytest.raises(utils.ImageIOLoadException):
        utils.check_mem(8, 1000)


def test_read_with_dask_txt(array_3D_as_2d_tiffs_path, array_3d):
    """
    Test that a series of images can be read correctly as a dask array
    """
    stack = load.read_with_dask(array_3D_as_2d_tiffs_path)
    np.testing.assert_array_equal(stack, array_3d)


def test_read_with_dask_glob_txt_equal(array_3D_as_2d_tiffs_path, txt_path):
    glob_stack = load.read_with_dask(array_3D_as_2d_tiffs_path)
    txt_stack = load.read_with_dask(txt_path)
    np.testing.assert_array_equal(glob_stack, txt_stack)


def test_read_z_stack_with_missing_metadata(
    array3d_as_tiff_stack_with_missing_metadata,
):
    with mock.patch(
        "brainglobe_utils.IO.image.load.logging.debug"
    ) as mock_debug:
        load.read_z_stack(str(array3d_as_tiff_stack_with_missing_metadata))
        mock_debug.assert_called_once()


def test_get_size_image_with_missing_metadata(
    array3d_as_tiff_stack_with_missing_metadata,
):
    with mock.patch(
        "brainglobe_utils.IO.image.load.logging.debug"
    ) as mock_debug:
        load.get_size_image_from_file_paths(
            str(array3d_as_tiff_stack_with_missing_metadata)
        )
        mock_debug.assert_called_once()
