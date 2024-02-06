import inspect
import sys
from string import ascii_letters, digits
from typing import Any, ClassVar, Dict

from brainglobe_utils.citation.format import Format


class BibTexEntry(Format):
    """
    An abstract base class for generating BibTex entries from
    CITATION.cff yaml-content.

    Constructed by passing a dict containing the yaml-processed
    content of the CITATION.cff file to the constructor.
    Required fields are checked for on instantiation.
    Missing optional fields will be set to None if not provided.

    Parameters
    ----------
    information : Dict[str, str]
        yaml-processed content of CITATION.cff.
    cite_key : str, default = "BrainGlobeReference"
        Citation key to add to the BibTex reference that is generated.
    warn_on_not_used: bool, default = False
        If True, warn the user about the fields in the information
        input that are not required nor optional, so are ignored.

    Attributes
    ----------
    cite_key : str
        The citation key that appears in the BibTex reference
    """

    author_separator: ClassVar[str] = " and "
    cite_key: str

    @classmethod
    def validate_citation_key(cls, key: str) -> bool:
        """
        Return True if the citation key provided is valid for use,
        otherwise return False.

        Valid citation keys may contain;
        - Alphanumeric characters,
        - Underscores (_),
        - Single dashes (-),
        - Semicolons (:),

        and no others.
        """
        bad_characters = key.lower()
        for valid_character in ascii_letters + digits + "_-:":
            bad_characters = bad_characters.replace(valid_character, "")

        if bad_characters:
            # Some characters in the string provided are not permitted,
            # as we have removed all of the permitted characters.
            return False
        return True

    def __init__(
        self,
        information: Dict[str, Any],
        cite_key: str = "BrainGlobeReference",
        warn_on_not_used: bool = False,
    ) -> None:
        """ """
        # So we don't delete information that we may need in other places
        # (C++ memory sharing rights plz Python)
        information = information.copy()

        # Add the citation key if provided,
        # or use the default otherwise
        if self.validate_citation_key(cite_key):
            self.cite_key = cite_key
        else:
            raise ValueError(
                f"Citation key {cite_key} is not valid."
                " Citation keys may only be composed of"
                "alphanumeric characters, digits, '_', '-', and ':'"
            )

        # If type information is available, ensure that we are reading
        # into the correct reference type!
        if "type" in information.keys():
            assert information["type"] == self.entry_type(), (
                "Attempting to read reference of type"
                f" {information['type']} into {self.entry_type()}"
            )
            # Remove type field from information dict,
            # so we don't try to assign it to a field later.
            information.pop("type")

        super().__init__(information, warn_on_not_used=warn_on_not_used)

        return

    def generate_ref_string(self) -> str:
        """
        Generate a string that encodes the reference, in preparation for
        writing to an output format.
        """
        output_string = f"@{self.entry_type()}{{{self.cite_key},\n"

        # Tracks current indentation level
        indent_level = 1

        # Required fields are guaranteed to exist
        for req_field in self.required:
            output_string += (
                self.indent_character * indent_level
                + f'{req_field} = "{getattr(self, req_field)}",\n'
            )

        # Optional fields may be skipped
        for opt_field in self.optional:
            if getattr(self, opt_field):
                output_string += (
                    self.indent_character * indent_level
                    + f'{opt_field} = "{getattr(self, opt_field)}",\n'
                )

        indent_level -= 1
        output_string += "}"

        return output_string


class Article(BibTexEntry):
    """
    Derived class for writing BibTex references to articles.
    """

    required = ["authors", "title", "journal", "year"]
    optional = [
        "volume",
        "number",
        "pages",
        "month",
        "note",
        "doi",
        "issn",
        "zblnumber",
        "eprint",
    ]


class Software(BibTexEntry):
    """
    Derived class for writing BibTex references to software.
    """

    required = ["authors", "title", "url", "year"]
    optional = [
        "abstract",
        "date",
        "doi",
        "eprint",
        "eprintclass",
        "eprinttype",
        "file",
        "hal_id",
        "hal_version",
        "institution",
        "license",
        "month",
        "note",
        "organization",
        "publisher",
        "related",
        "relatedtype",
        "relatedstring",
        "repository",
        "swhid",
        "urldate",
        "version",
    ]


def supported_bibtex_entry_types() -> Dict[str, BibTexEntry]:
    """
    Create a dict of all the classes in this module that can be used
    to write a bibtex reference of a particular entry type.

    keys are the entry type as it will appear in the .tex entry.
    values are the corresponding derived class to use when writing a
    reference of that type.

    Returns
    -------
    Dict[str, @_BibTexEntry]
        Dict of classes derived from BibTexEntry that can handle entry
        types, indexed by the entry type they support.
    """
    this_module = sys.modules[__name__]

    dict_of_formats: Dict[str, BibTexEntry] = {
        cls.entry_type(): cls
        for cls in (
            getattr(this_module, name)
            for name, _ in inspect.getmembers(this_module, inspect.isclass)
            if name != "BibTexEntry" and name != "Format"
        )
        if issubclass(cls, BibTexEntry)
    }

    return dict_of_formats
