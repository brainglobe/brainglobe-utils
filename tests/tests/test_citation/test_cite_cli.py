import subprocess
from typing import List

import pytest


def run_cite_brainglobe(*cli_args: str) -> subprocess.CompletedProcess:
    """
    Run the cite-brainglobe executable in the current environment,
    with the command line arguments provided.
    """
    completed_process: subprocess.CompletedProcess = subprocess.run(
        ["cite-brainglobe"] + list(cli_args),
        capture_output=True,
        text=True,
    )
    return completed_process


def test_smoke_cli() -> None:
    """
    Smoke test the citation CLI command.
    """
    completed_process = run_cite_brainglobe("--help")

    assert (
        completed_process.returncode == 0
    ), "Smoke test citation CLI exited with code: "
    f"{completed_process.returncode}.\n"
    f"STDERR capture: {completed_process.stderr}."


def test_catch_usage_error() -> None:
    """
    Check that a bad input to the command-line tool prints the help,
    and exits with code 2.
    """
    completed_process = run_cite_brainglobe("--bad-flag")

    # Should have returned with code 2
    assert (
        completed_process.returncode == 2
    ), "cite-brainglobe syntax error does not return code 2"
    # Should also have printed the help and usage pattern to stdout
    assert (
        "Citation generation for BrainGlobe tools" in completed_process.stdout
        and "usage: cite-brainglobe" in completed_process.stdout
    ), "cite-brainglobe syntax errors do not print help and usage."


@pytest.mark.parametrize(
    "error_msg, cli_args",
    [
        pytest.param(
            "Output format bad is not supported",
            ["-f", "bad"],
            id="No output file and unsupported format.",
        ),
        pytest.param(
            "does not support writing .foo files",
            ["-o", "brainglobe-citation.foo"],
            id="Output file with unsupported extension.",
        ),
        pytest.param(
            "have not provided a file extension nor citation format",
            ["-o", "brainglobe-citation"],
            id="Output file with no extension, and no format",
        ),
        pytest.param(
            "foo format is not supported, and your output file "
            "does not provide an implicit format",
            ["-o", "brainglobe-citation", "-f", "foo"],
            id="Output file with no extension, and unsupported format",
        ),
    ],
)
def test_catch_incompatible_args(error_msg: str, cli_args: List[str]) -> None:
    """
    Test disallowed combinations of format and output file inputs
    are correctly picked up.

    - If no output file is provided, format must be present and a supported
    format.
    - If output file is provided with an unsupported extension, error.
    - If output file is provided with no extension, and no format, error.
    - If output file is provided with no extension, and unsupported format,
    error.
    """
    # Cite at least one repository
    cli_args += ["brainglobe"]

    # Attempt citation creation
    completed_process = run_cite_brainglobe(*cli_args)
    assert (
        completed_process.returncode != 0
    ), "cite-brainglobe did not throw error, when it was expected to."
    assert error_msg in completed_process.stderr, (
        "cite-brainglobe correctly reports an error, "
        "but the reason is not the expected one."
    )
