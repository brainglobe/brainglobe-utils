import numpy as np

from .filter import smooth_opt


def peak_nd_array(array, smoothing_kernel=None):
    """
    Finds the max value of an array (with optional smoothing)
    :param np.array array: Input nD array
    :param smoothing_kernel: Smoothing kernel default: None
    :return: Maximum value
    """

    array = smooth_opt(array, smoothing_kernel=smoothing_kernel)
    peak_magnitude, _ = max_nd_array(array)
    return peak_magnitude


def max_nd_array(array):
    """
    Finds the location, and magnitude of the maximum value of an nD array.
    :param array: nD array
    :returns:
        - Magnitude of maximum value
        - Coordinates of maximum value
    """
    peak_location = np.unravel_index(array.argmax(), array.shape)
    peak_magnitude = array[peak_location]
    return peak_magnitude, peak_location
