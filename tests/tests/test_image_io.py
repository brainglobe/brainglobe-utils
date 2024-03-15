import random

import numpy as np
import pytest

from brainglobe_utils.image_io import load, save, utils


@pytest.fixture()
def array_2d():
    """Create a 4x4 array of 32-bit integers"""
    return np.tile(np.array([1, 2, 3, 4], dtype=np.int32), (4, 1))


@pytest.fixture()
def array_3d(array_2d):
    """Create a 4x4x4 array of 32-bit integers"""
    volume = np.stack((array_2d, 2 * array_2d, 3 * array_2d, 4 * array_2d))
    return volume


@pytest.fixture(params=["2D", "3D"])
def image_array(request, array_2d, array_3d):
    """Create both a 2D and 3D array of 32-bit integers"""
    if request.param == "2D":
        return array_2d
    else:
        return array_3d


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


def test_tiff_io(tmp_path, image_array):
    """
    Test that a 2D/3D tiff can be written and read correctly
    """
    dest_path = tmp_path / "image_array.tiff"
    save.save_any(image_array, dest_path)
    reloaded = load.load_any(dest_path)

    assert (reloaded == image_array).all()


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


@pytest.mark.parametrize(
    "load_parallel",
    [
        pytest.param(True, id="parallel loading"),
        pytest.param(False, id="no parallel loading"),
    ],
)
def test_tiff_sequence_io(tmp_path, array_3d, load_parallel):
    """
    Test that a 3D image can be written and read correctly as a sequence
    of 2D tiffs (with or without parallel loading)
    """
    save.save_any(array_3d, tmp_path)
    assert len(list(tmp_path.glob("*.tif"))) == array_3d.shape[0]

    reloaded_array = load.load_any(tmp_path, load_parallel=load_parallel)
    assert (reloaded_array == array_3d).all()


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
        assert (reloaded_array == array_3d).all()
    else:
        assert not (reloaded_array == array_3d).all()


def test_nii_io(tmp_path, array_3d):
    """
    Test that a 3D image can be written and read correctly as nii with scale
    (keeping it as a nifty object with no numpy conversion on loading)
    """
    nii_path = tmp_path / "test_array.nii"
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

    assert (reloaded_array == array_3d).all()


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


def test_image_size_txt(txt_path, array_3d):
    """
    Test that image size can be detected from a text file containing the paths
    of a sequence of 2D tiffs
    """
    image_shape = load.get_size_image_from_file_paths(txt_path)
    assert image_shape["x"] == array_3d.shape[2]
    assert image_shape["y"] == array_3d.shape[1]
    assert image_shape["z"] == array_3d.shape[0]
