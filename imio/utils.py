import psutil

import numpy as np

from scipy.ndimage import zoom


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

    volume = np.swapaxes(volume, 1, 2)
    volume = zoom(volume, (1, scaling_factor, 1), order=1)
    return np.swapaxes(volume, 1, 2)
