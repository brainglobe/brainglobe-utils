from typing import Dict, List, Union

import pytest

from brainglobe.citation.bibtex_fmt import Article


class TestFormat:
    """
    Tests for the Format class.

    We test on the Article class, since the Format class is a
    factory for the individual reference-writing classes so cannot
    be tested directly.

    But we can call the methods on a properly derived class.
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

    def test_bad_construction(self) -> None:
        """
        Test that:
        - Not providing a required key results in an error.
        - Providing an invalid authors format raises an error.
        - Providing a bad citation key raises an error.
        - Providing information with the wrong type field throws an error.
        """
        # Not providing a particular key
        pass_info = self.good_info.copy()
        pass_info.pop("authors", None)
        with pytest.raises(
            KeyError, match="Did not receive value for required key: authors"
        ):
            Article(information=pass_info)

        # Provide an invalid authors format
        pass_info[
            "authors"
        ] = "sensible name that's not in the expected format"
        with pytest.raises(
            TypeError,
            match="Expected authors to be either dict or list of dicts, "
            "not str",
        ):
            Article(information=pass_info)

        # Provide a list of invalid author formats
        pass_info["authors"] = [
            "sensible list",
            "of authors that",
            "isn't a bunch of dicts",
        ]
        with pytest.raises(
            TypeError,
            match="Expected individual author entry to be a dictionary, "
            "but it was str: .*",
        ):
            Article(information=pass_info)

        # Provide an invalid citation key
        with pytest.raises(ValueError, match="Citation key .* is not valid."):
            Article(information=self.good_info, cite_key="a11g00dt111n0w:(")

        # Read into the wrong reference type
        pass_info["authors"] = {
            "given-names": "now this",
            "family-names": "is all good",
        }
        pass_info["type"] = "software"
        with pytest.raises(
            AssertionError,
            match="Attempting to read reference of type software into article",
        ):
            Article(information=pass_info)

    def test_nothrow_on_missing_optionals(self) -> None:
        """
        Test that optional fields can be skipped when specifying information.
        """
        Article(information=self.good_info)

    def test_warn_on_unused_info(self) -> None:
        """
        Test that, when requested, warnings are thrown if information is
        passed that will not be used in the citation.
        """
        pass_info = self.good_info | self.opt_info
        pass_info["random_info"] = 42

        with pytest.warns(
            UserWarning,
            match="The key random_info is not used"
            " for entries of type article",
        ):
            Article(information=pass_info, warn_on_not_used=True)

    @pytest.mark.parametrize(
        "author_info, expected",
        [
            pytest.param(
                {"given-names": "T.", "family-names": "Ester"},
                "T. Ester",
                id="Standalone dict",
            ),
            pytest.param(
                [
                    {"given-names": "T.", "family-names": "Ester"},
                    {"given-names": "A Sr.", "family-names": "Developer"},
                ],
                "T. Ester and A Sr. Developer",
                id="List of dicts",
            ),
        ],
    )
    def test_author_parsing(
        self,
        author_info: Union[Dict[str, str], List[Dict[str, str]]],
        expected: str,
    ) -> None:
        """
        Test that authors information is parsed correctly when given as either
        a single dict, or a list of dicts.

        author_info is the information to be passed and processed by
        _prepare_author_field.
        expected is the string that we expect to be produced after this method
        returns.
        """
        pass_info = self.good_info.copy()
        pass_info["authors"] = author_info

        article = Article(pass_info, warn_on_not_used=True)

        assert article.authors == expected
