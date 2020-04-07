import numpy as np

pi = np.pi


def radial_bins(bin_size, degrees=True, remove_greater_than_360=False):
    """
    Given a bin size (width), divide a 360 degree radial distribution into
    bins (defined by edges). Only works properly when an integer number
    of bins fit into 360 degrees
    :param bin_size: Wdith of each bin
    :param degrees: If True, work in degrees, otherwise radians
    :param remove_greater_than_360: If there is not an integer number of
    bins in 360 degrees, what do to do with the last (>360 degree) bin.
    :return: np.array of bin edges
    """
    if degrees:
        bins = np.arange(0, 360 + bin_size, bin_size)
        max_permitted = 360
    else:
        bins = np.arange(0, 2 * pi + bin_size, bin_size)
        max_permitted = 2 * pi

    if remove_greater_than_360:
        if bins[-1] > max_permitted:
            bins = bins[0:-1]
    return bins


def opposite_angle(angle, degrees=True):
    """
    Returns the "opposite" angle. i.e 180 deg away from the input angle
    :param angle: Input angle in degrees
    :param degrees: If True, work in degrees, otherwise radians
    :return: "Opposite angle"
    """
    if degrees:
        if angle > 180:
            return angle - 180
        else:
            return angle + 180
    else:
        if angle > pi:
            return angle - pi
        else:
            return angle + pi


def phase_unwrap(degrees, discontinuity=180):
    """
    Unwraps phase discontinuity (i.e. adds or subtracts 180 deg when 0/360
    degrees is passed.
    :param degrees: Input angles in degrees
    :param discontinuity: Cut off of discontinuity to assume a phase wrap.
    Default: 180 degrees
    :return np.array: Unwrapped angles
    """
    discontinuity = np.deg2rad(discontinuity)
    rad = np.deg2rad(degrees)
    unwrap = np.unwrap(rad, discont=discontinuity)
    return np.rad2deg(unwrap)
