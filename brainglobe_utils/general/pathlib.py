from pathlib import Path


def append_to_pathlib_stem(path: Path, string_to_append: str):
    """
    Appends a string to the stem of a pathlib object.

    Parameters
    ----------
    path : pathlib.Path
        Pathlib path.

    string_to_append : str
        String to append to the stem.

    Returns
    -------
    pathlib.Path
        Pathlib object with the string added to the stem.
    """
    return path.parent / (path.stem + string_to_append + path.suffix)
