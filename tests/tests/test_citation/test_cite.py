from glob import glob
from pathlib import Path

import pytest

from brainglobe.citation.cite import cite


@pytest.mark.parametrize(
    "format",
    [
        pytest.param("bibtex", id="BibTex format"),
        pytest.param("text", id="Text format"),
    ],
)
def test_citation_combinations(
    format: str, newline_separations: int = 2
) -> None:
    """
    Test that when citing multiple tools, the resulting text is the
    combination of requesting the two tools individually.
    """

    both_together = cite(
        "brainglobe-meta",
        "bg-atlasapi",
        format=format,
        newline_separations=newline_separations,
    )
    bg_meta = cite("brainglobe-meta", format=format)
    bg_atlasapi = cite("bg-atlasapi", format=format)

    # Fetching both citations together should mean the text from the
    # individual citations is included
    assert bg_meta in both_together and bg_atlasapi in both_together, (
        "Fetching multiple tools at once"
        "does not generate all requested citations."
    )
    # Removing these individual blocks of text from the combined citation
    # should leave only newline and whitespace characters
    leftover_text = (
        both_together.replace(bg_meta, "")
        .replace(bg_atlasapi, "")
        .replace(" ", "")
        .replace("\n", "")
    )
    assert (
        not leftover_text
    ), f"Leftover text in combined citation: {leftover_text}"


def test_output_file_created(
    tmp_path, outfile_name: Path = Path("brainglobe-citation.tex")
) -> None:
    """
    Confirm that requesting an output file results in
    such a file being produced.
    """
    tmp_dir = tmp_path / "bg-cite-test"
    tmp_dir.mkdir()
    output_file = tmp_dir / outfile_name

    # Take stock of all files in the temporary directory write now
    all_files_present = [
        Path(f).relative_to(tmp_dir) for f in glob(f"{str(tmp_dir)}/*")
    ]
    # Run cite() and ask for an output file as above
    cite("brainglobe", format="bibtex", outfile=output_file)
    # Assert that the citation file has appeared
    all_files_present_post = [
        Path(f).relative_to(tmp_dir) for f in glob(f"{str(tmp_dir)}/*")
    ]

    # Assert the new file has been created
    new_files = set(all_files_present_post) - set(all_files_present)
    assert (
        len(new_files) == 1
    ), "No file produced when calling cite() with outfile argument."
    assert outfile_name in new_files, (
        "An output file was produced, but the name does not match that "
        f"which was expected: {[str(f) for f in new_files]}"
    )
