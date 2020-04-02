import argparse
import decimal


def is_even(num):
    """
    Returns True if a number is even
    :param num:
    :return:
    """
    if num == 0:
        raise NotImplementedError(
            "Input number is 0. Evenness of 0 is not defined by this "
            "function."
        )
    if num % 2:
        return False
    else:
        return True


def check_positive_float(value, none_allowed=True):
    """
    Used in argparse to enforce positive floats
    FromL https://stackoverflow.com/questions/14117415
    :param value: Input value
    :param none_allowed: If false, throw an error for None values
    :return: Input value, if it's positive
    """
    ivalue = value
    if ivalue is not None:
        ivalue = float(ivalue)
        if ivalue < 0:
            raise argparse.ArgumentTypeError(
                "%s is an invalid positive value" % value
            )
    else:
        if not none_allowed:
            raise argparse.ArgumentTypeError("%s is an invalid value." % value)

    return ivalue


def check_positive_int(value, none_allowed=True):
    """
    Used in argparse to enforce positive ints
    FromL https://stackoverflow.com/questions/14117415
    :param value: Input value
    :param none_allowed: If false, throw an error for None values
    :return: Input value, if it's positive
    """
    ivalue = value
    if ivalue is not None:
        ivalue = int(ivalue)
        if ivalue < 0:
            raise argparse.ArgumentTypeError(
                "%s is an invalid positive value" % value
            )
    else:
        if not none_allowed:
            raise argparse.ArgumentTypeError("%s is an invalid value." % value)

    return ivalue


def get_decimal_places(x):
    """
    Returns the number of decimal places of a number
    :param float x: Input number
    :return: Number of decimal places
    """
    d = decimal.Decimal(str(x))
    return abs(d.as_tuple().exponent)


def round_updown_to_x(num_in, x, direction="up"):
    """
    Rounds a given value (num_in) to the nearest multiple of x, in a given
    direction (up or down)
    :param num_in: Input value
    :param x: Value to round to a multiple of
    :param direction: Round up or down. Default: 'up'
    :return: Rounded number
    """
    if direction is "down":
        num_out = int(num_in) - int(num_in) % int(x)
    else:
        num_out = num_in + (x - num_in) % int(x)
    return num_out
