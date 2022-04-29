import tifffile
import warnings
import nrrd

import numpy as np


with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    import nibabel as nib


def to_nii(img, dest_path, scale=None, affine_transform=None):
    # TODO: see if we want also real units scale

    """
    Write the brain volume to disk as nifty image.

    :param img: A nifty image object or numpy array brain
    :param str dest_path: The path where to save the brain.
    :param tuple scale: A tuple of floats to indicate the 'zooms' of the nifty
        image
    :param np.ndarray affine_transform: A 4x4 matrix indicating the transform
        to save in the metadata of the image
        (required only if not nibabel input)
    :return:
    """
    dest_path = str(dest_path)
    if affine_transform is None:
        affine_transform = np.eye(4)
    if not isinstance(img, nib.Nifti1Image):
        img = nib.Nifti1Image(img, affine_transform)
    if scale is not None:
        img.header.set_zooms(scale)
    nib.save(img, dest_path)


def to_tiff(img_volume, dest_path):
    """
    Saves the image volume (numpy array) to a tiff stack

    :param np.ndarray img_volume: The image to be saved
    :param dest_path: Where to save the tiff stack
    """
    dest_path = str(dest_path)
    tifffile.imwrite(dest_path, img_volume)


def to_tiffs(img_volume, path_prefix, path_suffix="", extension=".tif"):
    """
    Save the image volume (numpy array) as a sequence of tiff planes.
    Each plane will have a filepath of the following for:
    pathprefix_zeroPaddedIndex_suffix.tif

    :param np.ndarray img_volume: The image to be saved
    :param str path_prefix:  The prefix for each plane
    :param str path_suffix: The suffix for each plane
    """
    z_size = img_volume.shape[0]
    pad_width = int(round(z_size / 10)) + 1
    for i in range(z_size):
        img = img_volume[i, :, :]
        dest_path = (
            f"{path_prefix}_{str(i).zfill(pad_width)}{path_suffix}{extension}"
        )
        tifffile.imwrite(dest_path, img)


def to_nrrd(img_volume, dest_path):
    """
    Saves the image volume (numpy array) as nrrd

    :param np.ndarray img_volume: The image to be saved
    :param dest_path: Where to save the nrrd image
    """
    dest_path = str(dest_path)
    nrrd.write(dest_path, img_volume)
