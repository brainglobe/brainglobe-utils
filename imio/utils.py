import logging
import psutil

from scipy.ndimage import zoom
from imlib.general.system import get_sorted_file_paths

import imio


class ImioLoadException(Exception):
    pass


def check_mem(img_byte_size, n_imgs):
    """
    Check how much memory is available on the system and compares it to the
    size the stack specified by img_byte_size and n_imgs would take
    once loaded

    Raises an error in case memory is insufficient to load that stack

    :param int img_byte_size: The size in bytes of an individual image plane
    :param int n_imgs: The number of image planes to load
    :raises: BrainLoadException if not enough memory is available
    """
    total_size = img_byte_size * n_imgs
    free_mem = psutil.virtual_memory().available
    if total_size >= free_mem:
        raise ImioLoadException(
            "Not enough memory on the system to complete loading operation"
            "Needed {}, only {} available.".format(total_size, free_mem)
        )


def scale_z(volume, scaling_factor):
    """
    Scale the given brain along the z dimension

    :param np.ndarray volume: A brain typically as a numpy array
    :param float scaling_factor:
    :return:
    """

    return zoom(volume, (scaling_factor, 1, 1), order=1)


def get_size_image_from_file_paths(file_path, file_extension="tif"):
    """
    Returns the size of an image (which is a list of 2D files), without loading
    the whole image
    :param str file_path: File containing file_paths in a text file,
    or as a list.
    :param str file_extension: Optional file extension (if a directory
     is passed)
    :return: Dict of image sizes
    """
    file_path = str(file_path)

    img_paths = get_sorted_file_paths(file_path, file_extension=file_extension)
    z_shape = len(img_paths)

    logging.debug(
        "Loading file: {} to check raw image size" "".format(img_paths[0])
    )
    image_0 = imio.load_any(img_paths[0])
    y_shape, x_shape = image_0.shape

    image_shape = {"x": x_shape, "y": y_shape, "z": z_shape}
    return image_shape
