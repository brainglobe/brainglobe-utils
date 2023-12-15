import os
import random
from pathlib import Path
from random import shuffle
from unittest.mock import patch

import pytest

from brainglobe_utils.general import system
from brainglobe_utils.general.string import get_text_lines

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


def test_replace_extension():
    test_file = "test_file.sh"
    test_ext = "txt"
    test_ext_w_dot = ".txt"
    validate_file = "test_file.txt"
    assert validate_file == system.replace_extension(test_file, test_ext)
    assert validate_file == system.replace_extension(test_file, test_ext_w_dot)


def test_remove_leading_character():
    assert ".ext" == system.remove_leading_character("..ext", ".")


def test_ensure_directory_exists(tmpdir):
    # string
    exist_dir = os.path.join(tmpdir, "test_dir")
    system.ensure_directory_exists(exist_dir)
    assert os.path.exists(exist_dir)
    os.rmdir(exist_dir)

    # pathlib
    exist_dir_pathlib = Path(tmpdir) / "test_dir2"
    system.ensure_directory_exists(exist_dir_pathlib)
    assert exist_dir_pathlib.exists()
    exist_dir_pathlib.rmdir()


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


def test_get_num_processes():
    cpu_count = 10
    with patch(
        "brainglobe_utils.general.system.psutil.cpu_count",
        return_value=cpu_count,
    ):
        assert system.get_num_processes(min_free_cpu_cores=0) == cpu_count


def test_max_processes():
    max_proc = 5
    correct_n = min(os.cpu_count(), max_proc)
    assert correct_n == system.get_num_processes(
        n_max_processes=max_proc, min_free_cpu_cores=0
    )


def test_max_processes_windows_low():
    cpu_count = 10
    with patch(
        "brainglobe_utils.general.system.platform.system",
        return_value="Windows",
    ):
        with patch(
            "brainglobe_utils.general.system.psutil.cpu_count",
            return_value=cpu_count,
        ):
            assert system.limit_cpus_windows(cpu_count) == cpu_count


def test_max_processes_windows_high():
    cpu_count = 128
    with patch(
        "brainglobe_utils.general.system.platform.system",
        return_value="Windows",
    ):
        with patch(
            "brainglobe_utils.general.system.psutil.cpu_count",
            return_value=cpu_count,
        ):
            # 61 is max on Windows
            assert system.limit_cpus_windows(cpu_count) == 61


class Paths:
    def __init__(self, directory):
        self.one = directory / "one.aaa"
        self.two = directory / "two.bbb"
        self.tmp__three = directory / "three.ccc"
        self.tmp__four = directory / "four.ddd"


def write_n_random_files(n, dir, min_size=32, max_size=2048):
    sizes = random.sample(range(min_size, max_size), n)
    for size in sizes:
        with open(os.path.join(dir, str(size)), "wb") as fout:
            fout.write(os.urandom(size))


def test_delete_directory_contents(tmpdir):
    delete_dir = os.path.join(str(tmpdir), "delete_dir")
    os.mkdir(delete_dir)
    write_n_random_files(10, delete_dir)

    # check the directory isn't empty first
    assert not os.listdir(delete_dir) == []

    system.delete_directory_contents(delete_dir, progress=True)
    assert os.listdir(delete_dir) == []
