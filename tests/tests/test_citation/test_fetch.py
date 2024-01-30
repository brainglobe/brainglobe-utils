import pytest

from brainglobe.citation.fetch import fetch_from_github


def test_fetch() -> None:
    """
    Test that content is fetched correctly when the url is valid,
    and a RuntimeError is thrown when the url is bad.
    """
    with pytest.raises(
        RuntimeError,
        match="Bad request or response, got .* when fetching from https://raw.githubusercontent.com/this/is-not/the/file/you.seek",
    ):
        fetch_from_github(
            user="this", repo="is-not", file="file/you.seek", branch="the"
        )

    # Check that we can fetch the README from this package's repository,
    # which we know should be there
    response = fetch_from_github("brainglobe", "brainglobe-meta", "README.md")

    assert response.ok, "Bad status code fetching brainglobe-meta readme file."
    assert "# BrainGlobe" in response.text
