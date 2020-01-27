from natsort import natsorted

from imlib.general import list


def get_text_lines(
    file,
    return_lines=None,
    rstrip=True,
    sort=False,
    remove_empty_lines=True,
    encoding=None,
):
    """
    Return only the nth line of a text file
    :param file: Any text file
    :param return_lines: Which specific line/lines to read
    :param rstrip: Remove trailing characters
    :param sort: If true, naturally sort the data
    :param remove_empty_lines: If True, ignore empty lines
    :param encoding: What encoding the text file has.
    Default: None (platform dependent)
    :return: The nth line
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
