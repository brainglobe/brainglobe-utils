import os
import platform
import random
import sys
from pathlib import Path
from random import shuffle
from unittest.mock import Mock, patch

import pytest

from brainglobe_utils.general import system
from brainglobe_utils.general.exceptions import CommandLineInputError
from brainglobe_utils.general.string import get_text_lines


@pytest.fixture
def cubes_dir(data_path):
    return data_path / "cubes"


@pytest.fixture
def jabberwocky(data_path):
    return data_path / "general" / "jabberwocky.txt"


@pytest.fixture
def jabberwocky_sorted(data_path):
    return data_path / "general" / "jabberwocky_sorted.txt"


@pytest.fixture
def sorted_cubes_dir(cubes_dir):
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

    return [str(cubes_dir / cube) for cube in cubes]


@pytest.fixture
def mock_disk_usage():
    """Fixture to mock shutil.disk_usage."""
    return Mock(
        return_value=(1000000, 500000, 500000)
    )  # total, used, free space in bytes


@pytest.fixture
def mock_statvfs():
    """Fixture to mock os.statvfs."""
    mock_stats = Mock()
    mock_stats.f_frsize = 1024  # Fragment size
    mock_stats.f_bavail = 1000  # Free blocks
    return mock_stats


def test_ensure_extension():
    assert system.ensure_extension("example.txt", ".txt") == Path(
        "example.txt"
    )
    assert system.ensure_extension(Path("example.txt"), ".txt") == Path(
        "example.txt"
    )

    assert system.ensure_extension("example.md", ".txt") == Path("example.txt")
    assert system.ensure_extension(Path("example.md"), ".txt") == Path(
        "example.txt"
    )

    assert system.ensure_extension("example", ".txt") == Path("example.txt")


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


def test_get_sorted_file_paths(
    cubes_dir, jabberwocky, jabberwocky_sorted, sorted_cubes_dir
):
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


def test_check_path_in_dir(jabberwocky, data_path):
    assert system.check_path_in_dir(jabberwocky, data_path / "general")


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
    mock_cpu_count = 128
    with patch(
        "brainglobe_utils.general.system.platform.system",
        return_value="Windows",
    ):
        with patch(
            "brainglobe_utils.general.system.psutil.cpu_count",
            return_value=mock_cpu_count,
        ):
            # 61 is max on Windows
            assert system.limit_cpus_windows(mock_cpu_count) == 61


@pytest.mark.parametrize("cores_available", [1, 100, 1000])
def test_cores_available_in_slurm_environment(cores_available):
    mock_slurm_parameters = Mock()
    mock_slurm_parameters.allocated_cores = cores_available

    with (
        patch.dict(
            "brainglobe_utils.general.system.os.environ", {"SLURM_JOB_ID": "1"}
        ),
        patch(
            "brainglobe_utils.general.system.slurmio.SlurmJobParameters",
            return_value=mock_slurm_parameters,
        ),
    ):
        assert system.get_cores_available() == cores_available


@pytest.mark.parametrize("cores_available", [1, 100, 1000])
def test_cores_available(cores_available):
    with patch(
        "brainglobe_utils.general.system.psutil.cpu_count",
        return_value=cores_available,
    ):
        assert system.get_cores_available() == cores_available


@pytest.mark.parametrize(
    "ram_needed_per_cpu, fraction_free_ram, max_ram_usage, "
    "free_system_ram, expected_cores",
    [
        (
            1024**3,
            0.1,
            None,
            16 * 1024**3,
            14,
        ),  # 1 GB per core, 0.1 fraction free, no max ram,
        # 16GB free on the system, expect 14
        (
            2 * 1024**3,
            0.5,
            None,
            256 * 1024**3,
            64,
        ),  # 1 GB per core, 0.5 fraction free, no max ram,
        # 256GB free on the system, expect 64
        (
            1024**3,
            0.5,
            10 * 1024**3,
            256 * 1024**3,
            5,
        ),  # 1 GB per core, 0.5 fraction free, 10Gb max ram,
        # 256GB free on the system, expect 5
    ],
)
def test_how_many_cores_with_sufficient_ram(
    ram_needed_per_cpu,
    fraction_free_ram,
    max_ram_usage,
    free_system_ram,
    expected_cores,
):
    with patch(
        "brainglobe_utils.general.system.get_free_ram",
        return_value=free_system_ram,
    ):
        assert (
            system.how_many_cores_with_sufficient_ram(
                ram_needed_per_cpu,
                fraction_free_ram,
                max_ram_usage=max_ram_usage,
            )
            == expected_cores
        )


def test_how_many_cores_with_sufficient_ram_in_slurm_environment():
    ram_needed_per_cpu = 1024**3  # 1 GB
    free_system_ram = 16 * 1024**3  # 16 GB

    mock_slurm_parameters = Mock()
    mock_slurm_parameters.allocated_memory = free_system_ram

    with (
        patch.dict(
            "brainglobe_utils.general.system.os.environ", {"SLURM_JOB_ID": "1"}
        ),
        patch(
            "brainglobe_utils.general.system.slurmio.SlurmJobParameters",
            return_value=mock_slurm_parameters,
        ),
    ):
        assert (
            system.how_many_cores_with_sufficient_ram(ram_needed_per_cpu) == 14
        )  # (0.9 * 16) GB / 1 GB per core


def test_disk_free_gb_windows(mock_disk_usage):
    with (
        patch(
            "brainglobe_utils.general.system.platform.system",
            return_value="Windows",
        ),
        patch(
            "brainglobe_utils.general.system.os.path.splitdrive",
            return_value=("C:\\", ""),
        ),
        patch(
            "brainglobe_utils.general.system.shutil.disk_usage",
            mock_disk_usage,
        ),
    ):
        free_space = system.disk_free_gb("C:\\path\\to\\file")
        assert free_space == 500000 / 1024**3


@pytest.mark.skipif(
    platform.system() == "Windows",
    reason="os.statvfs not available on Windows",
)
def test_disk_free_gb_linux(mock_statvfs):
    with (
        patch(
            "brainglobe_utils.general.system.platform.system",
            return_value="Linux",
        ),
        patch(
            "brainglobe_utils.general.system.os.statvfs",
            return_value=mock_statvfs,
        ),
    ):
        free_space = system.disk_free_gb("/path/to/file")
        assert free_space == (1024 * 1000) / 1024**3  # Free space in GB


@pytest.mark.skipif(
    platform.system() == "Windows",
    reason="os.statvfs not available on Windows",
)
def test_disk_free_gb_macos(mock_statvfs):
    with (
        patch(
            "brainglobe_utils.general.system.platform.system",
            return_value="Darwin",
        ),
        patch(
            "brainglobe_utils.general.system.os.statvfs",
            return_value=mock_statvfs,
        ),
    ):
        free_space = system.disk_free_gb("/path/to/file")
        assert free_space == (1024 * 1000) / 1024**3  # Free space in GB


def test_get_free_ram():
    mock_free_ram = 1000000001

    mock_virtual_memory = Mock()
    mock_virtual_memory.available = mock_free_ram

    with patch(
        "brainglobe_utils.general.system.psutil.virtual_memory",
        return_value=mock_virtual_memory,
    ):
        assert system.get_free_ram() == mock_free_ram


def write_n_random_files(n, dir, min_size=32, max_size=2048):
    sizes = random.sample(range(min_size, max_size), n)
    for size in sizes:
        with open(os.path.join(dir, str(size)), "wb") as fout:
            fout.write(os.urandom(size))


def test_delete_directory_contents_with_progress(tmp_path):
    delete_dir = tmp_path / "delete_dir"
    os.mkdir(delete_dir)
    write_n_random_files(10, delete_dir)

    # check the directory isn't empty first
    assert not os.listdir(delete_dir) == []

    system.delete_directory_contents(delete_dir, progress=True)
    assert os.listdir(delete_dir) == []


def test_delete_directory_contents(tmp_path):
    delete_dir = tmp_path / "delete_dir"
    os.mkdir(delete_dir)
    write_n_random_files(10, delete_dir)

    # check the directory isn't empty first
    assert not os.listdir(delete_dir) == []

    system.delete_directory_contents(delete_dir, progress=False)
    assert os.listdir(delete_dir) == []


def write_file_single_size(directory, file_size):
    with open(os.path.join(directory, str(file_size)), "wb") as fout:
        fout.write(os.urandom(file_size))


def test_check_path_exists(tmpdir):
    num = 10
    tmpdir = str(tmpdir)

    assert system.check_path_exists(os.path.join(tmpdir))
    no_exist_dir = os.path.join(tmpdir, "i_dont_exist")
    with pytest.raises(FileNotFoundError):
        assert system.check_path_exists(no_exist_dir)

    write_file_single_size(tmpdir, num)
    assert system.check_path_exists(os.path.join(tmpdir, str(num)))
    with pytest.raises(FileNotFoundError):
        assert system.check_path_exists(os.path.join(tmpdir, "20"))


def test_catch_input_file_error(tmpdir):
    tmpdir = str(tmpdir)
    # check no error is raised:
    system.catch_input_file_error(tmpdir)

    no_exist_dir = os.path.join(tmpdir, "i_dont_exist")
    with pytest.raises(CommandLineInputError):
        system.catch_input_file_error(no_exist_dir)


def test_safe_execute_command_str(tmp_path):
    log = tmp_path / "log.txt"
    err = tmp_path / "err.txt"

    cmd = f"{sys.executable} -c \"print('hello')\""

    system.safe_execute_command(
        cmd,
        log_file_path=str(log),
        error_file_path=str(err),
    )

    assert log.read_text().strip() == "hello"
    assert err.read_text() == ""


def test_safe_execute_command_list(tmp_path):
    log = tmp_path / "log.txt"
    err = tmp_path / "err.txt"

    cmd = [sys.executable, "-c", "print('hello')"]

    system.safe_execute_command(
        cmd,
        log_file_path=str(log),
        error_file_path=str(err),
    )

    assert log.read_text().strip() == "hello"
    assert err.read_text() == ""
