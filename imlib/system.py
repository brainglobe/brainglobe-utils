import os
import glob
from natsort import natsorted
from pathlib import Path, PosixPath

from imlib.string import get_text_lines


def ensure_directory_exists(directory):
    """
    If a directory doesn't exist, make it. Works for pathlib objects, and
    strings.
    :param directory:
    """
    if isinstance(directory, str):
        if not os.path.exists(directory):
            os.makedirs(directory)
    elif isinstance(directory, PosixPath):
        directory.mkdir(exist_ok=True)


def get_sorted_file_paths(file_path, file_extension=None, encoding=None):
    """
    Sorts file paths with numbers "naturally" (i.e. 1, 2, 10, a, b), not
    lexiographically (i.e. 1, 10, 2, a, b).
    :param str file_path: File containing file_paths in a text file,
    or as a list.
    :param str file_extension: Optional file extension (if a directory
     is passed)
    :param encoding: If opening a text file, what encoding it has.
    Default: None (platform dependent)
    :return: Sorted list of file paths
    """

    if isinstance(file_path, list):
        return natsorted(file_path)

    # assume if not a list, is a file path
    file_path = Path(file_path)
    if file_path.suffix == ".txt":
        return get_text_lines(file_path, sort=True, encoding=encoding)
    elif file_path.is_dir():
        if file_extension is None:
            file_path = glob.glob(os.path.join(file_path, "*"))
        else:
            file_path = glob.glob(
                os.path.join(file_path, "*" + file_extension)
            )
        return natsorted(file_path)

    else:
        message = (
            "Input file path is not a recognised format. Please check it "
            "is a list of file paths, a text file of these paths, or a "
            "directory containing image files."
        )
        raise NotImplementedError(message)


def check_path_in_dir(file_path, directory_path):
    """
    Check if a file path is in a directory
    :param file_path: Full path to a file
    :param directory_path: Full path to a directory the file may be in
    :return: True if the file is in the directory
    """
    directory = Path(directory_path)
    parent = Path(file_path).parent
    return parent == directory