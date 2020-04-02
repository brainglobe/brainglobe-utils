def opposite_angle_deg(angle):
    """
    Returns the "opposite" angle. i.e 180 deg away from the input angle
    :param angle: Input angle in degrees
    :return: "Opposite angle"
    """
    return 180 - abs(abs(angle - 180) - 180)
