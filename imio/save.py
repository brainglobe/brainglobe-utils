import tifffile
import warnings
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
    :return:
    """
    dest_path = str(dest_path)
    tifffile.imsave(dest_path, img_volume)


def to_tiffs(img_volume, path_prefix, path_suffix="", pad_width=4):
    """
    Save the image volume (numpy array) as a sequence of tiff planes.
    Each plane will have a filepath of the following for:
    pathprefix_zeroPaddedIndex_suffix.tif

    :param np.ndarray img_volume: The image to be saved
    :param str path_prefix:  The prefix for each plane
    :param str path_suffix: The suffix for each plane
    :param int pad_width: The number of digits on which the index of the
        image (z plane number) will be padded
    :return:
    """
    z_size = img_volume.shape[-1]
    if z_size > 10**pad_width:
        raise ValueError(
            "Not enough padding digits {} for value"
            " {}".format(pad_width, z_size)
        )
    for i in range(z_size):
        img = img_volume[:, :, i]
        dest_path = "{}_{}{}.tif".format(
            path_prefix, str(i).zfill(pad_width), path_suffix
        )
        tifffile.imsave(dest_path, img)
