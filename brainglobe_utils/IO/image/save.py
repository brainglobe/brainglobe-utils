import warnings
from pathlib import Path

import numpy as np
import tifffile

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    import nibabel as nib


def to_nii(img, dest_path, scale=None, affine_transform=None):
    # TODO: see if we want also real units scale

    """
    Write the brain volume to disk as a nifty image.

    Parameters
    ----------
    img : nifty image object or np.ndarray
        A nifty image object or numpy array representing a brain.

    dest_path : str or pathlib.Path
        The file path where to save the brain.

    scale : tuple of floats, optional
        A tuple of floats to indicate the 'zooms' of the nifty image.

    affine_transform : np.ndarray, optional
        A 4x4 matrix indicating the transform to save in the metadata of the
        image. Required only if not nibabel input.
    """
    dest_path = Path(dest_path)
    if affine_transform is None:
        affine_transform = np.eye(4)
    if not isinstance(img, nib.Nifti1Image):
        img = nib.Nifti1Image(img, affine_transform)
    if scale is not None:
        img.header.set_zooms(scale)
    nib.save(img, dest_path)


def to_tiff(img_volume, dest_path, photometric="minisblack"):
    """
    Save the image volume (numpy array) to a tiff stack.

    Parameters
    ----------
    img_volume : np.ndarray
        The image to be saved.

    dest_path : str or pathlib.Path
        The file path where to save the tiff stack.

    photometric: str
        Color space of image (to pass to tifffile.imwrite)
        Use 'minisblack' (default) for grayscale and 'rgb' for rgb
    """
    dest_path = Path(dest_path)
    tifffile.imwrite(
        dest_path,
        img_volume,
        photometric=photometric,
        metadata={"axes": "ZYX"},
    )


def to_tiffs(img_volume, path_prefix, path_suffix="", extension=".tif"):
    """
    Save the image volume (numpy array) as a sequence of tiff planes.
    Each plane will have a filepath of the following format:
    {path_prefix}_{zeroPaddedIndex}{path_suffix}{extension}

    Parameters
    ----------
    img_volume : np.ndarray
        The image to be saved.

    path_prefix : str or pathlib.Path
        The prefix for each plane.

    path_suffix : str, optional
        The suffix for each plane.

    extension : str, optional
        The file extension for each plane.
    """
    if isinstance(path_prefix, Path):
        path_prefix = str(path_prefix.resolve())

    z_size = img_volume.shape[0]
    pad_width = int(np.floor(np.log10(z_size)) + 1)
    for i in range(z_size):
        img = img_volume[i, :, :]
        dest_path = (
            f"{path_prefix}_{str(i).zfill(pad_width)}{path_suffix}{extension}"
        )
        tifffile.imwrite(dest_path, img)


def save_any(img_volume, dest_path):
    """
    Save the image volume (numpy array) to the given file path, using the save
    function matching its file extension.

    Parameters
    ----------
    img_volume : np.ndarray
        The image to be saved.

    dest_path : str or pathlib.Path
        The file path to save the image to.
        Supports directories (will save a sequence of tiffs), .tif, .tiff,
        and .nii.
    """
    dest_path = Path(dest_path)

    if dest_path.is_dir():
        to_tiffs(img_volume, dest_path / "image")

    elif dest_path.suffix in [".tif", ".tiff"]:
        to_tiff(img_volume, dest_path)

    elif dest_path.suffix == ".nii" or str(dest_path).endswith(".nii.gz"):
        to_nii(img_volume, dest_path)

    else:
        raise NotImplementedError(
            f"Could not guess data type for path {dest_path}"
        )


def save_as_asr_nii(
    stack: np.ndarray,
    vox_sizes: list,
    dest_path: Path,
):
    """
    Save 3D image stack to dest_path as a nifti image.

    This function assumes that the image is in the ASR orientation
    and sets the qform and sform of the nifti header accordingly
    (so that the image is displayed correctly in nifti viewers like ITK-SNAP).

    Parameters
    ----------
    stack : np.ndarray
        3D image stack
    vox_sizes : list
        list of voxel dimensions in mm, in the same order as the stack axes.
    dest_path : pathlib.Path
        path to save the nifti image
    """
    affine = _get_transf_matrix_from_res(vox_sizes)
    nii_img = nib.Nifti1Image(stack, affine, dtype=stack.dtype)
    # Set qform and sform to match axes orientation, assuming ASR
    reorient = np.array(
        [
            [0, 0, -1, 0],
            [-1, 0, 0, 0],
            [0, -1, 0, 0],
            [0, 0, 0, 1],
        ]
    )
    new_form = reorient @ affine
    nii_img.set_qform(new_form, code=3)
    nii_img.set_sform(new_form, code=3)
    # save the nifti image
    nib.save(nii_img, dest_path.as_posix())


def _get_transf_matrix_from_res(vox_sizes: list) -> np.ndarray:
    """Create transformation matrix from a dictionary of voxel dimensions.

    Parameters
    ----------
    vox_sizes : list
        list of voxel dimensions in mm, in the same order as the
        corresponding stack's axes.

    Returns
    -------
    np.ndarray
        A (4, 4) transformation matrix with the voxel dimensions
        on the first 3 diagonal entries.
    """
    transformation_matrix = np.eye(4)
    for i in range(3):
        transformation_matrix[i, i] = vox_sizes[i]
    return transformation_matrix
