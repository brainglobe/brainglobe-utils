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


def write_tiff_sequence_with_txt_file(txt_path, image_array):
    """
    Write an image array to a series of tiffs, and write a text file
    containing all the tiff file paths in order (one per line).

    The tiff sequence will be saved to a sub-folder inside the same folder
    as the text file.
    """
    directory = txt_path.parent

    # Write tiff sequence to sub-folder
    sub_dir = directory / "sub"
    sub_dir.mkdir()
    save.to_tiffs(image_array, str(sub_dir / "image_array"))

    # Write txt file containing all tiff file paths (one per line)
    txt_path.write_text(
        "\n".join(
            [str(sub_dir / fname) for fname in sorted(sub_dir.iterdir())]
        )
    )


def save_any(file_path, image_array):
    """
    Save image_array to given file path, using the save function matching
    its file extension
    """
    if file_path.is_dir():
        save.to_tiffs(image_array, str(file_path / "image_array"))

    elif file_path.suffix == ".txt":
        write_tiff_sequence_with_txt_file(file_path, image_array)

    elif file_path.suffix == ".tif" or file_path.suffix == ".tiff":
        save.to_tiff(image_array, file_path)

    elif file_path.suffix == ".nrrd":
        save.to_nrrd(image_array, file_path)

    elif file_path.suffix == ".nii":
        save.to_nii(image_array, file_path)


def test_single_2d_tifffile_io(tmp_path, layer):
    """
    Test that a 2D tiff can be written and read correctly with tifffile
    """
    dest_path = tmp_path / "layer.tiff"
    tifffile.imwrite(dest_path, layer)
    reloaded = tifffile.imread(dest_path)
    assert (reloaded == layer).all()


def test_single_3d_tiff_io(tmp_path, start_array):
    """
    Test that a 3D tiff can be written and read correctly with image_io
    """
    dest_path = tmp_path / "layer.tiff"
    save.to_tiff(start_array, dest_path)

    reloaded = load.load_img_stack(dest_path, 1, 1, 1)
    assert (reloaded == layer).all()


def test_tiff_sequence_io(tmp_path, start_array):
    """
    Test that a 3D image can be written and read correctly as a sequence
    of 2D tiffs
    """
    save.to_tiffs(start_array, str(tmp_path / "start_array"))
    reloaded_array = load.load_from_folder(str(tmp_path), 1, 1, 1)
    assert (reloaded_array == start_array).all()


def test_load_img_sequence_from_txt(tmp_path, start_array):
    """
    Test that a tiff sequence can be loaded from a text file containing an
    ordered list of the tiff file paths (one per line)
    """
    img_sequence_file = tmp_path / "imgs_file.txt"
    write_tiff_sequence_with_txt_file(img_sequence_file, start_array)

    # Load image from paths in text file
    reloaded_array = load.load_img_sequence(str(img_sequence_file), 1, 1, 1)
    assert (reloaded_array == start_array).all()


def test_nii_io(tmp_path, start_array):
    """
    Test that a 3D image can be written and read correctly as nii
    """
    nii_path = str(tmp_path / "test_array.nii")
    save.to_nii(start_array, nii_path, scale=(1, 1, 1))
    assert (load.load_nii(nii_path).get_fdata() == start_array).all()


def test_nrrd_io(tmp_path, start_array):
    """
    Test that a 3D image can be written and read correctly as nrrd
    """
    nrrd_path = str(tmp_path / "test_array.nrrd")
    save.to_nrrd(start_array, nrrd_path)
    assert (load.load_nrrd(nrrd_path) == start_array).all()


@pytest.mark.parametrize(
    "file_name",
    [
        "test_array.tiff",
        "test_array.tif",
        "test_array.txt",
        "test_array.nrrd",
        "test_array.nii",
        pytest.param("", id="dir of tiffs"),
    ],
)
def test_load_any(tmp_path, start_array, file_name):
    """
    Test that load_any can read all required image file types
    """
    src_path = tmp_path / file_name
    save_any(src_path, start_array)

    assert (load.load_any(src_path) == start_array).all()


def test_load_any_error(tmp_path):
    """
    Test that load_any throws an error for an unknown file extension
    """
    with pytest.raises(NotImplementedError):
        load.load_any(tmp_path / "test.unknown")


def test_scale_z(start_array):
    """
    Test that a 3D image can be scaled in z by float and integer values
    """
    assert utils.scale_z(start_array, 0.5).shape[0] == start_array.shape[0] / 2
    assert utils.scale_z(start_array, 2).shape[0] == start_array.shape[0] * 2
