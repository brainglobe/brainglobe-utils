import numpy as np


def pad_with_number_1d(array, final_length, pad_number=0):
    """
    For a given array, pad with a value (symmetrically on either side) so that
    the returned array is of a given length.
    :param np.array array: Input array.
    :param int final_length: How long should the final array be.
    :param (float, int) pad_number: What value to pad with. Default: 0.
    :return: New array of length: final_length
    """
    length = len(array)
    pad_length = int((final_length - length) / 2)
    pad = pad_number * np.ones((pad_length, 1))
    new_array = np.append(pad, array)
    new_array = np.append(new_array, pad)
    if len(new_array) < final_length:
        new_array = np.append(new_array, pad_number)

    return new_array
