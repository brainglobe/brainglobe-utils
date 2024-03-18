import argparse


def is_even(num):
    """
    Returns True if the non-zero input number is even.

    Parameters
    ----------
    num : int
        Input number.

    Returns
    -------
    bool
        True if number is even, otherwise False.

    Raises
    ------
    NotImplementedError
        If the input number is zero.
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
    Used in argparse to enforce positive floats.
    Source: https://stackoverflow.com/questions/14117415

    Parameters
    ----------
    value : float
        Input value.

    none_allowed : bool, optional
        If False, throw an error for None values.

    Returns
    -------
    float
        Input value, if it's positive.

    Raises
    ------
    argparse.ArgumentTypeError
        If input value is invalid.
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
    Used in argparse to enforce positive ints.
    Source: https://stackoverflow.com/questions/14117415

    Parameters
    ----------
    value : int
        Input value.

    none_allowed : bool, optional
        If False, throw an error for None values.

    Returns
    -------
    int
        Input value, if it's positive.

    Raises
    ------
    argparse.ArgumentTypeError
        If input value is invalid.
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
