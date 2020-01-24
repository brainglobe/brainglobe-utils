import pytest
import os

from pathlib import Path
from random import shuffle

from imlib import system
from imlib.string import get_text_lines


data_dir = Path("tests", "data")
cubes_dir = data_dir / "cubes"
jabberwocky = data_dir / "general" / "jabberwocky.txt"
jabberwocky_sorted = data_dir / "general" / "jabberwocky_sorted.txt"

cubes = [
    "pCellz222y2805x9962Ch1.tif",
    "pCellz222y2805x9962Ch2.tif",
    "pCellz258y3892x10559Ch1.tif",
    "pCellz258y3892x10559Ch2.tif",
    "pCellz413y2308x9391Ch1.tif",
    "pCellz413y2308x9391Ch2.tif",
    "pCellz416y2503x5997Ch1.tif",
    "pCellz416y2503x5997Ch2.tif",
    "pCellz418y5457x9489Ch1.tif",
    "pCellz418y5457x9489Ch2.tif",
    "pCellz433y4425x7552Ch1.tif",
    "pCellz433y4425x7552Ch2.tif",
]

sorted_cubes_dir = [os.path.join(str(cubes_dir), cube) for cube in cubes]


def test_ensure_directory_exists():
    home = os.path.expanduser("~")
    exist_dir = os.path.join(home, ".test_dir")
    system.ensure_directory_exists(exist_dir)
    assert os.path.exists(exist_dir)
    os.rmdir(exist_dir)


def test_get_sorted_file_paths():
    # test list
    shuffled = sorted_cubes_dir.copy()
    shuffle(shuffled)
    assert system.get_sorted_file_paths(shuffled) == sorted_cubes_dir

    # test dir
    assert system.get_sorted_file_paths(cubes_dir) == sorted_cubes_dir
    assert (
        system.get_sorted_file_paths(cubes_dir, file_extension=".tif")
        == sorted_cubes_dir
    )

    # test text file
    # specifying utf8, as written on linux
    assert system.get_sorted_file_paths(
        jabberwocky, encoding="utf8"
    ) == get_text_lines(jabberwocky_sorted, encoding="utf8")

    # test unsupported
    with pytest.raises(NotImplementedError):
        system.get_sorted_file_paths(shuffled[0])


def test_check_path_in_dir():
    assert system.check_path_in_dir(jabberwocky, data_dir / "general")
