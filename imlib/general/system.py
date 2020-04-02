import os
import glob
import logging
import psutil
import platform
import shutil
import subprocess
from tqdm import tqdm

from slurmio import slurmio
from natsort import natsorted
from pathlib import Path, PosixPath
from tempfile import gettempdir

from imlib.general.string import get_text_lines


def replace_extension(file, new_extension, check_leading_period=True):
    """
    Replaces the file extension of a given file
    :param str file: Input file with file extension to replace
    :param str new_extension: New file extension
    :param bool check_leading_period: If True, any leading period of the
    new extension is removed, preventing "file..txt"
    :return str: File with new file extension
    """
    if check_leading_period:
        new_extension = remove_leading_character(new_extension, ".")
    return os.path.splitext(file)[0] + "." + new_extension


def remove_leading_character(string, character):
    """
    If "string" starts with "character", strip that leading character away.
    Only removes the first instance
    :param string:
    :param character:
    :return: String without the specified, leading character
    """
    if string.startswith(character):
        return string[1:]
    else:
        return string


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


def get_num_processes(
    min_free_cpu_cores=2,
    ram_needed_per_process=None,
    fraction_free_ram=0.1,
    n_max_processes=None,
    max_ram_usage=None,
):
    """
    Determine how many CPU cores to use, based on a minimum number of cpu cores
    to leave free, and an optional max number of processes.

    Cluster computing aware for the SLURM job scheduler, and not yet
    implemented for other environments.
    :param int min_free_cpu_cores: How many cpu cores to leave free
    :param float ram_needed_per_process: Memory requirements per process. Set
    this to ensure that the number of processes isn't too high.
    :param float fraction_free_ram: Fraction of the ram to ensure stays free
    regardless of the current program.
    :param int n_max_processes: Maximum number of processes
    :param float max_ram_usage: Maximum amount of RAM (in bytes)
    to use (allthough available may be lower)
    :return: Number of processes to
    """
    logging.debug("Determining the maximum number of CPU cores to use")
    try:
        os.environ["SLURM_JOB_ID"]
        n_cpu_cores = (
            slurmio.SlurmJobParameters().allocated_cores - min_free_cpu_cores
        )
    except KeyError:
        n_cpu_cores = psutil.cpu_count() - min_free_cpu_cores

    logging.debug(f"Number of CPU cores available is: {n_cpu_cores}")

    if ram_needed_per_process is not None:
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
    else:
        n_processes = n_cpu_cores

    if n_max_processes is not None:
        if n_max_processes < n_processes:
            logging.debug(
                f"Forcing the number of processes to {n_max_processes} based"
                f" on other considerations."
            )
        n_processes = min(n_processes, n_max_processes)

    logging.debug(f"Setting number of processes to: {n_processes}")
    return int(n_processes)


def how_many_cores_with_sufficient_ram(
    ram_needed_per_cpu, fraction_free_ram=0.1, max_ram_usage=None
):
    """
    Based on the amount of RAM needed per CPU core for a multiprocessing task,
    work out how many CPU cores could theoretically be used based on the
    amount of free RAM. N.B. this does not relate to how many CPU cores
    are actually available.

    :param float ram_needed_per_cpu: Memory requirements per process. Set
    this to ensure that the number of processes isn't too high.
    :param float fraction_free_ram: Fraction of the ram to ensure stays free
    regardless of the current program.
    :param float max_ram_usage: Maximum amount of RAM (in bytes)
    to use (allthough available may be lower)
    :return: How many CPU cores could be theoretically used based on
    the amount of free RAM
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
    :param file_path: File path on the disk to be checked
    :return: Free space in GB
    """
    if platform.system() == "Windows":
        drive, _ = os.path.splitdrive(file_path)
        total, used, free = shutil.disk_usage(drive)
        return free / 1024 ** 3
    else:
        stats = os.statvfs(file_path)
        return (stats.f_frsize * stats.f_bavail) / 1024 ** 3


def get_free_ram():
    """
    Returns the amount of free RAM in bytes
    :return: Available RAM in bytes
    """
    return psutil.virtual_memory().available


def sanitize_num_processes(num_processes, min_processes, parallel=False):
    """
    Returns False to prevent parallel processing in case more processes have
    been requested than can be used.
    :param num_processes: How many processes have been requested
    :param min_processes: Minimum number of cores to keep free
    :param parallel: If parallel is requested
    :return bool: True if num_processes is sensible
    """
    if parallel:
        if num_processes < min_processes:
            parallel = False
    return parallel


def safe_execute_command(cmd, log_file_path=None, error_file_path=None):
    """
    Executes a command in the terminal, making sure that the output can
    be logged even if execution fails during the call.

    :param cmd:
    :param log_file_path:
    :param error_file_path:
    :return:
    """
    if log_file_path is None:
        log_file_path = os.path.abspath(
            os.path.join(gettempdir(), "safe_execute_command.log")
        )
    if error_file_path is None:
        error_file_path = os.path.abspath(
            os.path.join(gettempdir(), "safe_execute_command.err")
        )

    with open(log_file_path, "w") as log_file, open(
        error_file_path, "w"
    ) as error_file:
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


def delete_temp(directory, paths, prefix="tmp__"):
    """
    Removes all temp files (properties of an object starting with "tmp__")
    :param directory: Directory to delete tmp files from
    :param paths: Paths object with temp paths.
    :param prefix: String that temporary files (to be deleted) begin with.
    """
    for path_name, path in paths.__dict__.items():
        if path_name.startswith(prefix):
            if check_path_in_dir(path, directory):
                try:
                    os.remove(path)
                except FileNotFoundError:
                    logging.debug(
                        f"File: {path} not found, not deleting. "
                        f"Proceeding anyway."
                    )


def delete_directory_contents(directory, progress=False):
    """
    Removes all contents of a directory
    :param directory: Directory with files to be removed
    """
    files = os.listdir(directory)
    if progress:
        for f in tqdm(files):
            os.remove(os.path.join(directory, f))
    else:
        for f in files:
            os.remove(os.path.join(directory, f))


def filename_from_path(path, remove_extension=False):
    """
    Takes a filepath and returns only the filename, optionally removes the
    file extension
    :param path: Filepath
    :param remove_extension: If True, remove the file extension too.
    Default: False
    :return: filename
    """

    filename = os.path.basename(path)
    if remove_extension:
        filename = os.path.splitext(filename)[0]
    return filename
