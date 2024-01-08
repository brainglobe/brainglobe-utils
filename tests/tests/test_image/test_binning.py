import numpy as np

from brainglobe_utils.image import binning


def test_get_bins():
    image_size = (1000, 20, 125, 725)
    bin_sizes = (500, 2, 25, 100)

    dim0_bins = np.array((0, 500, 1000))
    dim1_bins = np.array((0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20))
    dim2_bins = np.array((0, 25, 50, 75, 100, 125))
    dim3_bins = np.array((0, 100, 200, 300, 400, 500, 600, 700))
    bins = binning.get_bins(image_size, bin_sizes)

    assert (dim0_bins == bins[0]).all()
    assert (dim1_bins == bins[1]).all()
    assert (dim2_bins == bins[2]).all()
    assert (dim3_bins == bins[3]).all()
