import numpy as np


def opposite_angle_deg(angle):
    """
    Returns the "opposite" angle. i.e 180 deg away from the input angle
    :param angle: Input angle in degrees
    :return: "Opposite angle"
    """
    return 180 - abs(abs(angle - 180) - 180)


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
