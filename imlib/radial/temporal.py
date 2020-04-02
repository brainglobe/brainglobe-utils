import numpy as np


def angle_bin_occupancy(angles, angles_per_sec, bin_size=6, normalise=False):
    """
    For a list of angles (in degrees), and how many angle values are sampled
    per second, return the occupancy (in seconds) of each of those bins.
    :param angles: Array of angle values in degrees
    :param angles_per_sec: How many angle values are recorded each second
    :param bin_size: Bin size. Default: 6 degrees
    :param bool normalise: Normalise the distribution to unit area.
    Default: False
    :return: Bin occupancy (in seconds), and bin central values (in degrees)
    """

    head_angles_in_bin, b = np.histogram(
        angles, bins=np.arange(0, 360 + bin_size, bin_size), density=normalise
    )
    bin_centers = np.deg2rad(np.ediff1d(b) // 2 + b[:-1])
    angle_occupancy = head_angles_in_bin / angles_per_sec

    return angle_occupancy, bin_centers
