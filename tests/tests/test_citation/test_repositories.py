import pytest

from brainglobe_utils.citation.repositories import (
    Repository,
    all_citable_repositories,
    unique_repositories_from_tools,
)


def test_throw_on_bad_repo() -> None:
    """
    Test that we cannot construct a repository that doesn't exist.
    """
    with pytest.raises(
        ValueError, match="Repository brainglobe/dont-exist does not exist"
    ):
        Repository("dont-exist", ["a", "b", "c"])

    with pytest.raises(
        TypeError, match="Cannot convert input of type int to a set"
    ):
        Repository("BrainGlobe", 76)


def test_repository_basics() -> None:
    """
    Test the following features of the Repository class:

    - Repository urls are constructed correctly
    - The equality comparison (by the repo url)
    - The less-than comparison (by repo name)
    """
    BrainGlobe = Repository("BrainGlobe", [])
    bg_atlasapi = Repository("bg-atlasapi", [])

    # URL construction
    assert BrainGlobe.url == "https://github.com/brainglobe/BrainGlobe"

    # Equality comparison
    assert (
        BrainGlobe != bg_atlasapi
    ), "Different repositories are deemed equal!"
    assert (
        BrainGlobe == BrainGlobe
    ), "Identical repositories are deemed unequal!"

    # Less-than and ordering (alphabetical by Python)
    assert (
        BrainGlobe < bg_atlasapi
    ), "Repository comparison does not assert alphabetical order by name"


def test_alias_syntax() -> None:
    """
    Test that the in keyword behaves as expected for determining if a
    tool resides inside a repository.
    """
    r = Repository("BrainGlobe", ["BG"])

    # Explicit alias that was included, case-insensitive
    assert "bG" in r, "Could not located expected tool alias."
    # Repository name itself should be an implicit alias
    assert "brainglobe" in r, "Could not use repository name as tool alias."
    # Not an alias will return false
    assert "not-an-alias" not in r, "Unexpected alias present in class."


def test_unique_repos() -> None:
    """
    Test the unique_repositories_from_tools function, in the following ways:

    - Duplicate entries are removed
    - Errors are thrown if the repository does not exist
    - We can successfully find all of the brainglobe repositories we define.
    """
    # Test that duplicates are removed if referred to twice
    assert (
        len(
            unique_repositories_from_tools(
                "bg-atlasapi", "bg_atlasapi", report_duplicates=True
            )
        )
        == 1
    ), "Duplicates are not removed when asking for unique repositories."

    # Test that non-existent brainglobe repositories raise an error
    with pytest.raises(
        RuntimeError,
        match="No citable repository found for tool future-bg-tool.*",
    ):
        unique_repositories_from_tools("future-bg-tool")

    # Test that we actually find all of our repositories, if we ask for them
    all_our_repositories = all_citable_repositories()
    our_fetchable_repositories = unique_repositories_from_tools(
        *[r.name for r in all_our_repositories]
    )
    assert all_our_repositories == our_fetchable_repositories


def test_automatic_alias_generation() -> None:
    """
    Test that the aliases that are automatically generated
    given the repository name are indeed added to the set of
    known aliases.

    - The -, _, and " " characters are all interchangeable
    - The brainglobe prefix is dropped if present in a new alias.
    """
    # Create Repository, providing an alias distinct from the package name
    meta_package = Repository("brainglobe-meta", "my_alias")

    # "meta" alias should be available since brainglobe prefix is present
    assert (
        "meta" in meta_package.tool_aliases
    ), "brainglobe prefix not dropped to make new alias."

    # "brainglobe meta" and "brainglobe_meta" should also have been added
    # as valid aliases
    assert (
        "brainglobe meta" in meta_package.tool_aliases
        and "brainglobe_meta" in meta_package.tool_aliases
    ), "Interchangeable characters in name are not replaced."

    # The custom alias should also have seen automatic additions, replacing
    # the underscore character
    assert (
        "my alias" in meta_package.tool_aliases
        and "my-alias" in meta_package.tool_aliases
    ), "Interchangeable characters in custom aliases are not replaced."
