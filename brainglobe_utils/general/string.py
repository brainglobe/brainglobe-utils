from natsort import natsorted

from brainglobe_utils.general import list


def get_text_lines(
    file,
    return_lines=None,
    rstrip=True,
    sort=False,
    remove_empty_lines=True,
    encoding="utf8",
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
