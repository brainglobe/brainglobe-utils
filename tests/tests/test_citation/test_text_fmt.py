from brainglobe.citation.text_fmt import TextCitation


def test_generate_ref_string() -> None:
    """
    Test that the expected output string is written when assembling a
    TextCitation.
    """
    required_info = {
        "authors": [{"given-names": "tester", "family-names": "testing"}],
        "title": "testing",
        "year": 2000,
    }
    opt_info = {
        "journal": "journal of testing",
        "volume": "1",
        "number": 42,
        "pages": "42",
        "month": "test",
        "note": "test",
        "doi": "test-doi",
        "issn": "420",
        "zblnumber": "test",
        "eprint": "test",
        "citation-sentence": "We are testing this class",
    }
    pass_info = required_info | opt_info

    text_citation = TextCitation(pass_info, warn_on_not_used=False)

    generated_text = text_citation.generate_ref_string()
    lines_of_text = generated_text.split("\n")

    # Should have produced exactly 3 lines of text given that
    # we provided a citation sentence and optional info
    assert len(lines_of_text) == 3

    # First line should be the citation sentence ended with a semicolon
    assert lines_of_text[0] == f"{opt_info['citation-sentence']};"
    # Second line should be the required info in sentence form
    assert (
        lines_of_text[1] == f"tester testing ({required_info['year']}). "
        f"{required_info['title']}."
    ), f"TextCitation has invalid required info format: {lines_of_text[1]}"
    # Final line should be assembled from the optional information provided
    # We didn't provide a URL, so this should be missing.
    # Final comma that's trailing should also have been removed.
    expected_format = (
        f"{opt_info['journal']}, "
        f"{opt_info['volume']}({opt_info['issn']}), "
        f"{opt_info['doi']}"
    )
    assert lines_of_text[-1] == expected_format, (
        f"TextCitation does not display optional info correctly; "
        f"{lines_of_text[-1]}"
    )
