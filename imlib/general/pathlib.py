def append_to_pathlib_stem(path, string_to_append):
    """
    Appends a string to the stem of a pathlib object
    :param path: pathlib path
    :param string_to_append:  string to append to the stem
    :return: pathlib object with the string added to the stem
    """
    return path.parent / (path.stem + string_to_append + path.suffix)
