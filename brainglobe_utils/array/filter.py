import scipy.ndimage.filters as filters


def smooth_opt(array, smoothing_kernel=None, smoothing_type="gaussian"):
    """
    Smoothes an array, but does nothing is smoothing=None
    :param array: Input nD array
    :param smoothing_kernel: Smoothing kernel default: None
    :param smoothing_type: How to smooth, e.g. "gaussian"
    :return: (Possibly) smoothed array
    """
    if smoothing_kernel is not None:
        if smoothing_type == "gaussian":
            array = filters.gaussian_filter(array, smoothing_kernel)
        else:
            raise ValueError(
                f"Smoothing type: '{smoothing_type}' is not " f"supported"
            )
    return array
