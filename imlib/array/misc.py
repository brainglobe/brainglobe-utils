import numpy as np


def sanitise_array(array, extreme_multiplier=None, exclude_zeros=False):
    """
    Remove nans and other extreme values, including those introduced by
    np.nan_to_num
    :param array: nD numpy array
    :param extreme_multiplier: How extreme (compared to median) are values
    allowed to be?
    :param bool exclude_zeros: If True, don't include zero values in the
    median value calculation. Default: False
    :return np.array: Array with extreme values removed
    """
    array = np.nan_to_num(array)
    if extreme_multiplier is not None:
        array = reject_extreme(
            array, extreme_multiplier, exclude_zeros=exclude_zeros
        )
    return array


def reject_extreme(array, extreme_multiplier, exclude_zeros=False):
    """
    Removes extremely large values from an array (by setting to 0).

    Useful following numpy.nan_to_num which replaces NaN values with very
    large (10^300) values.
    :param np.array array: Input array
    :param extreme_multiplier: What multiple of the median value is classed
    as "extreme"
    :param bool exclude_zeros: If True, don't include zero values in the
    median value calculation. Default: False
    :return np.array: Array with the "extreme values" set to 0
    """
    if exclude_zeros:
        array[
            abs(array / np.median(array[array != 0])) > extreme_multiplier
        ] = 0
    else:
        array[abs(array / np.median(array)) > extreme_multiplier] = 0
    return array


def mask_array_by_array_val(in_array, test_array, min_val):
    """
    Sets elements of array to 0, where test_array < min_val
    :param in_array: array to be manipulated
    :param test_array: array in which min_val must be reached. must be same
    dimensions as in_array
    :param min_val: value test_array must reach
    :return: masked array
    """

    in_array[test_array < min_val] = 0
    return in_array
