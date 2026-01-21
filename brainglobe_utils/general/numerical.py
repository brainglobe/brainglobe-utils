import argparse
from typing import Literal


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


def check_positive_float(
    value: float | None | Literal["None", "none"],
    none_allowed: bool = True,
) -> float | None:
    """
    Used in argparse to enforce positive floats.
    Source: https://stackoverflow.com/questions/14117415

    Parameters
    ----------
    value : float or None
        Input value.

    none_allowed : bool, optional
        If False, throw an error for None values.

    Returns
    -------
    float or None
        Input value, if it's positive, or None.

    Raises
    ------
    argparse.ArgumentTypeError
        If input value is invalid.
    """
    ivalue = value
    if value in (None, "None", "none"):
        if not none_allowed:
            raise argparse.ArgumentTypeError(f"{ivalue} is an invalid value.")
        value = None
    else:
        value = float(value)
        if value < 0:
            raise argparse.ArgumentTypeError(
                f"{ivalue} is an invalid positive value"
            )

    return value


def check_positive_int(
    value: int | None | Literal["None", "none"], none_allowed: bool = True
) -> int | None:
    """
    Used in argparse to enforce positive ints.
    Source: https://stackoverflow.com/questions/14117415

    Parameters
    ----------
    value : int or None
        Input value.

    none_allowed : bool, optional
        If False, throw an error for None values.

    Returns
    -------
    int or None
        Input value, if it's positive, or None.

    Raises
    ------
    argparse.ArgumentTypeError
        If input value is invalid.
    """
    ivalue = value
    if value in (None, "None", "none"):
        if not none_allowed:
            raise argparse.ArgumentTypeError(f"{ivalue} is an invalid value.")
        value = None
    else:
        value = int(value)
        if value < 0:
            raise argparse.ArgumentTypeError(
                f"{ivalue} is an invalid positive value"
            )

    return value
