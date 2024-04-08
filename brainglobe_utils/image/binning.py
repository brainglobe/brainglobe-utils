import numpy as np


def get_bins(image_size, bin_sizes):
    """
    Given an image size, and bin size, return a list of the bin boundaries.

    Parameters
    ----------
    image_size : tuple of int or list of int
        Size of the final image
    bin_sizes : tuple of int or list of int
        Bin sizes corresponding to the dimensions of "image_size"

    Returns
    -------
    list of np.ndarray
        List of arrays of bin boundaries
    """
    bins = []
    for dim in range(0, len(image_size)):
        bins.append(np.arange(0, image_size[dim] + 1, bin_sizes[dim]))
    return bins
