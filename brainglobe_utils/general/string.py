import argparse
from pathlib import Path
from typing import Optional

from natsort import natsorted

from brainglobe_utils.general import list


def get_text_lines(
    file: Path,
    return_lines: Optional[int] = None,
    rstrip: Optional[bool] = True,
    sort: Optional[bool] = False,
    remove_empty_lines: Optional[bool] = True,
    encoding: Optional[str] = "utf8",
):
    """
    Return only the nth line of a text file.

    Parameters
    ----------
    file : str or pathlib.Path
        Path to any text file.

    return_lines : int, optional
        Which specific line to read.

    rstrip : bool, optional
        Whether to remove trailing characters.

    sort : bool, optional
        If True, naturally sort the data.

    remove_empty_lines : bool, optional
        If True, ignore empty lines.

    encoding : str, optional
        What encoding the text file has.

    Returns
    -------
    str or list of str
        The nth line or lines.
    """
    with open(file, encoding=encoding) as f:
        lines = f.readlines()
    if rstrip:
        lines = [line.strip() for line in lines]
    if remove_empty_lines:
        lines = list.remove_empty_string(lines)
    if sort:
        lines = natsorted(lines)
    if return_lines is not None:
        lines = lines[return_lines]
    return lines


def check_str(value, none_allowed=True):
    """
    Used in argparse to enforce str input.

    Parameters
    ----------
    value : str or None
        Input value.

    none_allowed : bool, optional
        If False, throw an error for None values.

    Returns
    -------
    str or None
        Input value, if it's str, or None.

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
        value = str(value)

    return value
