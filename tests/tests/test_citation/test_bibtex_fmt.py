from typing import List

import pytest

from brainglobe_utils.citation.bibtex_fmt import (
    Article,
    supported_bibtex_entry_types,
)


@pytest.fixture()
def entry_types_we_support() -> List[str]:
    """
    All Bibtex entry types that we support for writing BrainGlobe references.
    """
    return ["article", "software"]


def test_supported_entry_types(entry_types_we_support) -> None:
    """
    Check that we support all the entry types that we are expecting to.
    """
    dict_of_classes = supported_bibtex_entry_types()
    list_of_entry_types = sorted(list(dict_of_classes.keys()))

    assert sorted(list_of_entry_types) == sorted(entry_types_we_support), (
        "Mismatch between entry types we expect to support, "
        "and those we actually do.\n"
        f"Expect to support: {sorted(entry_types_we_support)}"
        f"Actually supporting: {sorted(list_of_entry_types)}"
    )
    return


def test_generate_ref_string() -> None:
    """
    Test that the expected output string is written when assembling a
    Bibtex entry.

    We test on the Article class, but are really only calling methods
    from the base BibtexEntry class.
    """
    good_info = {
        "authors": [{"given-names": "tester", "family-names": "testing"}],
        "title": "testing",
        "journal": "tested",
        "year": 2000,
    }
    opt_info = {
        "volume": "test",
        "number": 42,
        "pages": "42",
        "month": "test",
        "note": "test",
        "doi": "test",
        "issn": "test",
        "zblnumber": "test",
        "eprint": "test",
    }
    pass_info = good_info | opt_info | {"type": "article"}
    citation_key = "TESTING123"

    article = Article(pass_info, cite_key=citation_key, warn_on_not_used=False)

    generated_text = article.generate_ref_string()
    lines_of_text = generated_text.split("\n")

    # Length of lines_of_text should be at least
    # 2 (cite-key header and closing bracer) + number of required fields
    # lines long
    assert len(lines_of_text) >= 2 + len(article.required)

    # First line should be @<type>{<cite_key>,
    assert lines_of_text[0] == f"@article{{{citation_key},"
    # Final line should be the closing bracer only
    assert lines_of_text[-1] == "}"

    # Intermediary lines are a bit trickier,
    # but they should all be of the form
    # <indent><field> = "<value>"
    # with the "authors" field having a slightly different value
    intermediary_lines = lines_of_text[1:-1]
    potential_fields = article.required + article.optional

    for key, value in pass_info.items():
        if key != "authors":
            expected_line = f'{article.indent_character}{key} = "{value}",'
        else:
            # Hard-code expected authors pre-processing,
            # tested above in test_author_parsing
            expected_line = (
                f'{article.indent_character}authors = "tester testing",'
            )

        # Check that this is at least one of the lines,
        # if there is the possibility that the information should be
        # included in the reference.
        if key in potential_fields:
            # Annoying PEP8 mypy formatting things
            error_line = (
                f"Value corresponding to {key} "
                "missing from generated string."
            )
            assert expected_line in intermediary_lines, error_line
        # Otherwise, assert that information that was not needed
        # has been ignored
        else:
            error_line = (
                f"Information for {key} was included in generated string"
                " when it should have been ignored."
            )
            assert expected_line not in intermediary_lines, error_line
