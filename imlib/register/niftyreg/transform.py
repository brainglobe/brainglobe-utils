from imlib.source.niftyreg_binaries import get_binary, get_niftyreg_binaries
from imlib.general.exceptions import TransformationError

from imlib.general.system import (
    safe_execute_command,
    SafeExecuteCommandError,
)


def run_transform(
    floating_image_path,
    output_file_name,
    destination_image_filename,
    control_point_file,
    log_file_path,
    error_file_path,
):

    transformation_cmd = prepare_transformation_cmd(
        floating_image_path,
        output_file_name,
        destination_image_filename,
        control_point_file,
    )

    safe_transform(transformation_cmd, log_file_path, error_file_path)


def prepare_transformation_cmd(
    floating_image_path,
    output_file_name,
    destination_image_filename,
    control_point_file,
    program_name="reg_resample",
    program_path=None,
    nifty_reg_binaries_folder=None,
):
    if program_path is None:
        if nifty_reg_binaries_folder is None:
            nifty_reg_binaries_folder = get_niftyreg_binaries()
        program_path = get_binary(nifty_reg_binaries_folder, program_name)

    cmd = "{} -cpp {} -flo {} -ref {} -res {}".format(
        program_path,
        control_point_file,
        floating_image_path,
        destination_image_filename,
        output_file_name,
    )
    return cmd


def safe_transform(transformation_command, log_file_path, error_file_path):
    """
    Using a specified niftyreg command, transforms an image, and catches
    any logs or errors.
    :param str transformation_command: Full niftyreg command
    :param log_file_path: Path to save the log file to
    :param error_file_path: Path to save the error file to
    """
    try:
        safe_execute_command(
            transformation_command, log_file_path, error_file_path
        )
    except SafeExecuteCommandError as err:
        raise TransformationError("Transformation failed; {}".format(err))
