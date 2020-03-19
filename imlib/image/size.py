import numpy as np
from scipy.ndimage import zoom


def resize_array(array, target_size, order=0):
    """
    Resizes an array to a target size. Uses less RAM than skimage
    implementation
    :param np.array array: numpy array to be resized
    :param tuple target_size: target size of array
    :param int order: Order for the interpolation (e.g. 0 for nearest
    neighbours)
    :return: Resized numpy array
    """
    factors = np.asarray(target_size, dtype=float) / np.asarray(
        array.shape, dtype=float
    )
    array = zoom(array, factors, order=order)
    return array
