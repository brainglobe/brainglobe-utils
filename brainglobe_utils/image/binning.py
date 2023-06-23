import numpy as np


def get_bins(image_size, bin_sizes):
    """
    Given an image size, and bin size, return a list of the bin boundaries
    :param image_size: Size of the final image (tuple/list)
    :param bin_sizes: Bin sizes corresponding to the dimensions of
    "image_size" (tuple/list)
    :return: List of arrays of bin boundaries
    """
    bins = []
    for dim in range(0, len(image_size)):
        bins.append(np.arange(0, image_size[dim], bin_sizes[dim]))
    return bins
