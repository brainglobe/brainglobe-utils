import warnings
from typing import Any, ClassVar, Dict, List, Union


class Format:
    """
    An abstract base class for generating reference formats
    from CITATION.cff yaml-content.

    Constructed by passing a dict containing the yaml-processed
    content of the CITATION.cff file to the constructor.
    Required fields are checked for on instantiation.
    Missing optional fields will be set to None if not provided.

    Parameters
    ----------
    information : Dict[str, str]
        yaml-processed content of CITATION.cff.
    warn_on_not_used: bool, default = False
        If True, warn the user about the fields in the information
        input that are not required nor optional, so are ignored.

    Attributes
    ----------
    author_separator : str, default = ", "
        Separator to use between authors in the event the reference
        has more than one author provided.
    indent_character : str, default = ' ' * 4
        Character sequence to use for indentation.
    required : ClassVar[List[str]]
        Required fields for the entry to be created.
    optional : ClassVar[List[str]]
        Optional fields that the entry may possess.
    """

    indent_character: str = " " * 4
    author_separator: ClassVar[str] = ", "
    required: ClassVar[List[str]]
    optional: ClassVar[List[str]]

    # mypy type-hints
    authors: Union[str, Dict[str, str], List[Dict[str, str]]]

    @classmethod
    def entry_type(cls) -> str:
        """
        The reference format type; article, book, software, etc.
        This will be inherited by child classes and used to infer
        which format the citation.cff files are providing.
        """
        return cls.__name__.lower()

    def __init__(
        self,
        information: Dict[str, Any],
        warn_on_not_used: bool = False,
    ) -> None:
        """ """
        # So we don't delete information that we may need in other places
        # (C++ memory sharing rights plz Python)
        information = information.copy()

        # Add all the information we need
        for key, value in information.items():
            if key in self.required or key in self.optional:
                setattr(self, key.replace("-", "_"), value)
            elif warn_on_not_used:
                warnings.warn(
                    f"The key {key} is not used for entries of type "
                    f"{self.entry_type()}",
                    UserWarning,
                )

        # Check that all required information is populated
        for required_field in self.required:
            if not hasattr(self, required_field):
                raise KeyError(
                    f"Did not receive value for required key: {required_field}"
                )
        # Optional fields should be set to None so that checks against
        # them produce nothing and evaluate to False
        for optional_field in self.optional:
            if not hasattr(self, optional_field.replace("-", "_")):
                setattr(self, optional_field.replace("-", "_"), None)

        if hasattr(self, "authors"):
            self._prepare_authors_field()

        return

    def _prepare_authors_field(self) -> None:
        """
        The authors field may come in as a dict, or a list of dicts.
        This is rather inconvenient as we need it to be a string, so
        convert it with this function.

        Individual author fields in CITATION.cff are:
        - family-names
        - given-names
        - orcid
        - affiliation

        of which we only need the names.
        """
        # A single author will be read in as a dictionary
        if isinstance(self.authors, dict):
            surname = self.authors["family-names"]
            forename = self.authors["given-names"]
            self.authors = f"{forename} {surname}"
        # Multiple authors will be read in as a list of dictionaries
        elif isinstance(self.authors, list):
            all_authors = []
            for author_info in self.authors:
                if not isinstance(author_info, dict):
                    raise TypeError(
                        "Expected individual author entry to be "
                        "a dictionary, but it was "
                        f"{type(author_info).__name__}: {author_info}"
                    )
                else:
                    surname = author_info["family-names"]
                    forename = author_info["given-names"]
                    all_authors.append(f"{forename} {surname}")
            self.authors = self.author_separator.join(all_authors)
        # Unrecognised read format, abort
        else:
            raise TypeError(
                f"Expected authors to be either dict or list of dicts,"
                f" not {type(self.authors).__name__}"
            )
        return

    def generate_ref_string(self) -> str:
        """
        Generate the citation text from the information provided,
        in the given format.

        This method will be overwritten by the derived class that
        manages the format.
        """
        pass
