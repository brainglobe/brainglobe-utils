import glob
import logging
import os
import platform
import shutil
import subprocess
from pathlib import Path
from tempfile import gettempdir
from typing import Union

import psutil
from natsort import natsorted
from slurmio import slurmio
from tqdm import tqdm

from brainglobe_utils.general.exceptions import CommandLineInputError
from brainglobe_utils.general.string import get_text_lines

# On Windows, max_workers must be less than or equal to 61
# https://docs.python.org/3/library/concurrent.futures.html#processpoolexecutor
MAX_PROCESSES_WINDOWS = 61


def ensure_extension(
    file_path: Union[str, os.PathLike], extension: str
) -> Path:
    """
    Ensure that the given file path has the specified extension.

    If the file path does not already have the specified extension,
    it changes the file path to have that extension.

    Parameters
    ----------
    file_path : Union[str, os.PathLike]
        The path to the file.
    extension : str
        The desired file extension (should include the dot, e.g., '.txt').

    Returns
    -------
    Path
        The Path object with the ensured extension.
    """
    path = Path(file_path)
    if path.suffix != extension:
        path = path.with_suffix(extension)
    return path


def replace_extension(file, new_extension, check_leading_period=True):
    """
    Replaces the file extension of a given file.

    Parameters
    ----------
    file : str
        Input file path with file extension to replace.

    new_extension : str
        New file extension.

    check_leading_period : bool, optional
        If True, any leading period of the new extension is removed,
        preventing "file..txt".

    Returns
    -------
    str
        File path with new file extension.
    """
    if check_leading_period:
        new_extension = remove_leading_character(new_extension, ".")
    return os.path.splitext(file)[0] + "." + new_extension


def remove_leading_character(string, character):
    """
    If "string" starts with "character", strip that leading character away.
    Only removes the first instance.

    Parameters
    ----------
    string : str
        Input string.

    character : str
        Character to be stripped if found at the beginning of the string.

    Returns
    -------
    str
        String without the specified leading character.
    """
    if string.startswith(character):
        return string[1:]
    else:
        return string


def ensure_directory_exists(directory):
    """
    If a directory doesn't exist, make it. Works for pathlib objects,
    and strings.

    Parameters
    ----------
    directory : str or pathlib.Path
        Directory to be created if it doesn't exist.
    """
    if isinstance(directory, str):
        if not os.path.exists(directory):
            os.makedirs(directory)
    elif isinstance(directory, Path):
        directory.mkdir(exist_ok=True)


def get_sorted_file_paths(file_path, file_extension=None, encoding=None):
    """
    Sorts file paths with numbers "naturally" (i.e. 1, 2, 10, a, b), not
    lexicographically (i.e. 1, 10, 2, a, b).

    Parameters
    ----------
    file_path : list of str or str or pathlib.Path
        List of file paths, or path of a text file containing these paths,
        or path of a directory containing files.

    file_extension : str, optional
        Only return filepaths with this extension (if a directory is passed).

    encoding : str, optional
        If opening a text file, what encoding it has.
        Default is None (platform dependent).

    Returns
    -------
    list of str
        Sorted list of file paths.
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
    Check if a file path is in a directory.

    Parameters
    ----------
    file_path : str or pathlib.Path
        Full path to a file.

    directory_path : str or pathlib.Path
        Full path to a directory the file may be in.

    Returns
    -------
    bool
        True if the file is in the directory, False otherwise.
    """
    directory = Path(directory_path)
    parent = Path(file_path).parent
    return parent == directory


def get_num_processes(
    min_free_cpu_cores=2,
    ram_needed_per_process=None,
    fraction_free_ram=0.1,
    n_max_processes=None,
    max_ram_usage=None,
    enforce_single_cpu=True,
):
    """
    Determine how many CPU cores to use, based on a minimum number of CPU cores
    to leave free, and an optional maximum number of processes.

    Cluster computing aware for the SLURM job scheduler, and not yet
    implemented for other environments.

    Parameters
    ----------
    min_free_cpu_cores : int, optional
        How many CPU cores to leave free.

    ram_needed_per_process : float, optional
        Memory requirements per process. Set this to ensure that the number of
        processes isn't too high.

    fraction_free_ram : float, optional
        Fraction of the RAM to ensure stays free regardless of the current
        program.

    n_max_processes : int, optional
        Maximum number of processes.

    max_ram_usage : float, optional
        Maximum amount of RAM (in bytes) to use (although available may be
        lower).

    enforce_single_cpu : bool, optional
        Ensure that >=1 CPU core is chosen.

    Returns
    -------
    int
        Number of processes to use.
    """
    logging.debug("Determining the maximum number of CPU cores to use")

    n_cpu_cores = get_cores_available()
    n_cpu_cores = n_cpu_cores - min_free_cpu_cores

    logging.debug(f"Number of CPU cores available is: {n_cpu_cores}")

    if ram_needed_per_process is not None:
        n_processes = limit_cores_based_on_memory(
            n_cpu_cores,
            ram_needed_per_process,
            fraction_free_ram,
            max_ram_usage,
        )
    else:
        n_processes = n_cpu_cores

    n_max_processes = limit_cpus_windows(n_max_processes)

    if n_max_processes is not None:
        if n_max_processes < n_processes:
            logging.debug(
                f"Limiting the number of processes to {n_max_processes} based"
                f" on other considerations."
            )
        n_processes = min(n_processes, n_max_processes)

    if enforce_single_cpu:
        if n_processes < 1:
            logging.debug("Forcing number of processes to be 1")
            n_processes = 1

    logging.debug(f"Setting number of processes to: {n_processes}")
    return int(n_processes)


def limit_cpus_windows(n_max_processes):
    if platform.system() == "Windows":
        if n_max_processes is not None:
            n_max_processes = min(n_max_processes, MAX_PROCESSES_WINDOWS)
    return n_max_processes


def get_cores_available():
    try:
        os.environ["SLURM_JOB_ID"]
        n_cpu_cores = slurmio.SlurmJobParameters().allocated_cores
    except KeyError:
        n_cpu_cores = psutil.cpu_count()

    return n_cpu_cores


def limit_cores_based_on_memory(
    n_cpu_cores, ram_needed_per_process, fraction_free_ram, max_ram_usage
):
    cores_w_sufficient_ram = how_many_cores_with_sufficient_ram(
        ram_needed_per_process,
        fraction_free_ram=fraction_free_ram,
        max_ram_usage=max_ram_usage,
    )
    n_processes = min(n_cpu_cores, cores_w_sufficient_ram)
    logging.debug(
        f"Based on memory requirements, up to {cores_w_sufficient_ram} "
        f"cores could be used. Therefore setting the number of "
        f"processes to {n_processes}."
    )
    return n_processes


def how_many_cores_with_sufficient_ram(
    ram_needed_per_cpu, fraction_free_ram=0.1, max_ram_usage=None
):
    """
    Based on the amount of RAM needed per CPU core for a multiprocessing task,
    work out how many CPU cores could theoretically be used based on the
    amount of free RAM. N.B. this does not relate to how many CPU cores
    are actually available.

    Parameters
    ----------
    ram_needed_per_cpu : float
        Memory requirements per process. Set this to ensure that the number of
        processes isn't too high.

    fraction_free_ram : float, optional
        Fraction of the RAM to ensure stays free regardless of the current
        program.

    max_ram_usage : float, optional
        The Maximum amount of RAM (in bytes) to use (although available may be
        lower).

    Returns
    -------
    int
        How many CPU cores could be theoretically used based on the amount of
        free RAM.
    """

    try:
        # if in slurm environment
        os.environ["SLURM_JOB_ID"]
        # Only allocated memory (not free). Assumes that nothing else will be
        # running
        free_mem = slurmio.SlurmJobParameters().allocated_memory
    except KeyError:
        free_mem = get_free_ram()

    logging.debug(f"Free memory is: {free_mem} bytes.")

    if max_ram_usage is not None:
        free_mem = min(free_mem, max_ram_usage)
        logging.debug(
            f"Maximum memory has been set as: {max_ram_usage} "
            f"bytes, so using: {free_mem} as the maximum "
            f"available memory"
        )

    free_mem = free_mem * (1 - fraction_free_ram)
    cores_w_sufficient_ram = free_mem / ram_needed_per_cpu
    return int(cores_w_sufficient_ram // 1)


def disk_free_gb(file_path):
    """
    Return the free disk space, on a disk defined by a file path.

    Parameters
    ----------
    file_path : str
        File path on the disk to be checked.

    Returns
    -------
    float
        Free space in GB.
    """
    if platform.system() == "Windows":
        drive, _ = os.path.splitdrive(file_path)
        total, used, free = shutil.disk_usage(drive)
        return free / 1024**3
    else:
        stats = os.statvfs(file_path)
        return (stats.f_frsize * stats.f_bavail) / 1024**3


def get_free_ram():
    """
    Returns the amount of free RAM in bytes.

    Returns
    -------
    int
        Available RAM in bytes.
    """
    return psutil.virtual_memory().available


def safe_execute_command(cmd, log_file_path=None, error_file_path=None):
    """
    Executes a command in the terminal, making sure that the output can
    be logged even if execution fails during the call.

    From https://github.com/SainsburyWellcomeCentre/amap_python by
    Charly Rousseau (https://github.com/crousseau).

    Parameters
    ----------
    cmd : str
        Command to be executed.

    log_file_path : str, optional
        File path to log the output.

    error_file_path : str, optional
        File path to log any errors.
    """
    if log_file_path is None:
        log_file_path = os.path.abspath(
            os.path.join(gettempdir(), "safe_execute_command.log")
        )
    if error_file_path is None:
        error_file_path = os.path.abspath(
            os.path.join(gettempdir(), "safe_execute_command.err")
        )

    with (
        open(log_file_path, "w") as log_file,
        open(error_file_path, "w") as error_file,
    ):
        try:
            subprocess.check_call(
                cmd, stdout=log_file, stderr=error_file, shell=True
            )
        except subprocess.CalledProcessError:
            hline = "-" * 25
            try:
                with open(error_file_path, "r") as err_file:
                    errors = err_file.readlines()
                    errors = "".join(errors)
                with open(log_file_path, "r") as _log_file:
                    logs = _log_file.readlines()
                    logs = "".join(logs)
                raise SafeExecuteCommandError(
                    "\n{0}\nProcess failed:\n {1}"
                    "{0}\n"
                    "{2}\n"
                    "{0}\n"
                    "please read the logs at {3} and {4}\n"
                    "{0}\n"
                    "command: {5}\n"
                    "{0}".format(
                        hline,
                        errors,
                        logs,
                        log_file_path,
                        error_file_path,
                        cmd,
                    )
                )
            except IOError as err:
                raise SafeExecuteCommandError(
                    f"Process failed: please read the logs at {log_file_path} "
                    f"and {error_file_path}; command: {cmd}; err: {err}"
                )


class SafeExecuteCommandError(Exception):
    pass


def delete_directory_contents(directory, progress=False):
    """
    Removes all contents of a directory.

    Parameters
    ----------
    directory : str
        Directory with files to be removed.

    progress : bool, optional
        Whether to show a progress bar.
    """
    files = os.listdir(directory)
    if progress:
        for f in tqdm(files):
            os.remove(os.path.join(directory, f))
    else:
        for f in files:
            os.remove(os.path.join(directory, f))


def check_path_exists(file):
    """
    Returns True if a file exists, otherwise throws a FileNotFoundError.

    Parameters
    ----------
    file : str or pathlib.Path
        Input file.

    Returns
    -------
    bool
        True if the file exists.

    Raises
    ------
    FileNotFoundError
        If the file doesn't exist.
    """
    file = Path(file)
    if file.exists():
        return True
    else:
        raise FileNotFoundError


def catch_input_file_error(path):
    """
    Catches if an input path doesn't exist, and returns an informative error.

    Parameters
    ----------
    path : str or pathlib.Path
        Input file path.

    Raises
    ------
    CommandLineInputError
        If the file doesn't exist.
    """
    try:
        check_path_exists(path)
    except FileNotFoundError:
        message = (
            "File path: '{}' cannot be found. Please check your input "
            "arguments.".format(path)
        )
        raise CommandLineInputError(message)
