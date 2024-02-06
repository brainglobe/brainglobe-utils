import sys
from argparse import ArgumentParser
from pathlib import Path
from typing import Literal
from warnings import warn

from brainglobe_utils.citation.bibtex_fmt import (
    BibTexEntry,
    supported_bibtex_entry_types,
)
from brainglobe_utils.citation.repositories import (
    all_citable_repositories,
    unique_repositories_from_tools,
)
from brainglobe_utils.citation.text_fmt import TextCitation

FORMAT_TO_EXTENSION = {"bibtex": "tex", "text": "txt"}
EXTENSION_TO_FORMAT = {
    value: key for key, value in FORMAT_TO_EXTENSION.items()
}


def cite(
    *tools: str,
    format: Literal["bibtex", "text"] = "text",
    outfile: Path = None,
    cite_software: bool = False,
    newline_separations: int = 2,
    warn_on_unused_info: bool = False,
) -> str:
    """
    Provide citation(s) for the BrainGlobe tool(s) that the user has supplied.

    If two or more aliases point to the same tool, remove duplicates and report
    the duplication has been ignored.

    Parameters
    ----------
    tools: str
        Tool names or aliases that are to be cited.
    format: One of bibtex, default = bibtex
        Reference format to write.
    outfile: str, default = None
        The output file to write to, if provided.
        If None, reference text will be printed to the console.
    cite_software: bool, default = False
        If True, software citations will be preferred over the article
        or journal counterparts, where present in repositories.
        Use if you want to reference the source code of a particular tool,
        rather than acknowledge use of the tool itself.
    newline_separations: int, default = 2
        Number of newline characters to use when separating references, in the
        event that multiple tools are to be cited.
    warn_on_unused_info: bool, default = False
        If True, information parsed from the yaml-content that is not used by
        the citation format will be flagged to the user on output.

    Returns
    -------
    str
        The string of citation text that was produced, in the requested format.

    Raises
    ------
    ValueError
        If the citation data fetched is missing a type specifier, and the
        format requested requires this to be explicitly set.
    """
    unique_repos = unique_repositories_from_tools(
        *tools, report_duplicates=True
    )

    # unique_repos is now a set of all the repositories that we need to cite
    # so we just need to gather all the citations we need
    cite_string = ""

    for repo in unique_repos:
        # Fetch citation information from repository
        citation_info = repo.read_citation_info()

        # Some formats are citation-type agnostic, others are not
        # Attempt to read this key here, and set the value to None
        # if it's not present.
        # This ensures that users don't have to provide the field if
        # they want to cite something that doesn't need the information.
        try:
            citation_type = citation_info["type"]
        except KeyError as e:
            warn(
                f"{repo.name} has no citation type data - "
                "reference may not be generated correctly.\n"
                f"(Caught {str(e)})",
                UserWarning,
            )
            citation_type = None

        # The repo_reference variable will contain the reference string
        repo_reference: str = None

        # Check if there is a preferred-citation field,
        # and whether we want to use that information over the standard
        # software citation.
        # Note that if the alternative citation is also a software
        # citation, it will still be rendered as such.
        if (
            citation_type == "software"
            and not cite_software
            and "preferred-citation" in citation_info.keys()
        ):
            citation_info = citation_info["preferred-citation"]
            citation_type = citation_info["type"]

        # Determine citation format in preparation for writing
        if format == "text":
            # If the user requested the citation sentence,
            # provide this by looking up the expected field.
            reference_instance = TextCitation(
                citation_info, warn_on_not_used=warn_on_unused_info
            )
        else:
            # We need to convert the citation information to
            # a particular format

            # Cite this repository in the desired format
            if format == "bibtex":
                try:
                    citation_class = supported_bibtex_entry_types()[
                        citation_type
                    ]
                except KeyError:
                    raise ValueError(
                        f"Bibtex entries require a supported Bibtex entry type"
                        " to be provided in citation metadata "
                        f"(got {citation_type})"
                    )

                reference_instance: BibTexEntry = citation_class(
                    citation_info,
                    cite_key=f"{repo.name}",
                    warn_on_not_used=warn_on_unused_info,
                )

        # Append the reference to the string we are generating
        repo_reference = reference_instance.generate_ref_string()
        cite_string += f"{repo_reference}" + "\n" * newline_separations

    # Upon looping over each of the repositories, we should be ready to dump
    # the output to the requested location.
    if outfile is not None:
        # Write output to file
        with open(Path(outfile), "w") as output_file:
            output_file.write(cite_string)
    else:
        sys.stdout.write(cite_string)

    return cite_string


class BrainGlobeParser(ArgumentParser):
    """
    Overwrite argparse default behaviour to have usage errors
    print the command-line tool help, rather than throwing the
    error encountered.
    """

    def error(self, msg):
        sys.stderr.write(f"Error: {msg}\nSee usage instructions below:\n")
        self.print_help()
        sys.exit(2)


def cli() -> None:
    """
    Command-line interface for the citation tool.
    """
    parser = BrainGlobeParser(
        description="Citation generation for BrainGlobe tools."
    )

    parser.add_argument(
        "-l",
        "--list",
        action="store_true",
        help="List citable BrainGlobe tools, and formats, then exit.",
    )
    parser.add_argument(
        "-s",
        "--software-citations",
        action="store_true",
        help="Explicitly cite software source code over academic papers.",
    )
    parser.add_argument(
        "-w",
        "--warn-unused",
        action="store_true",
        help="Print out when citation information is omitted by "
        "the chosen citation format.",
    )
    parser.add_argument(
        "-o",
        "--output-file",
        type=str,
        default=None,
        help="Output file to write citations to.",
    )
    parser.add_argument(
        "-f",
        "--format",
        type=str,
        default=None,
        help="Citation format to write. "
        "Will be overwritten by the inferred format if the output file "
        "argument is also provided. "
        "Valid formats can be listed with the -l, --list option.",
    )
    parser.add_argument(
        "tools", nargs="*", type=str, help="BrainGlobe tools to be cited."
    )

    arguments = parser.parse_args()

    # Check if we just want to list available options
    if arguments.list:
        # List citable BrainGlobe tools
        sys.stdout.write("Citable BrainGlobe tools by name (source code):\n")
        for repo in sorted(all_citable_repositories()):
            sys.stdout.write(f"\t- {repo.name} ({repo.url})\n")

        # List reference formats
        sys.stdout.write(
            "Available citation formats "
            "(supported file extension), format option:\n"
        )
        sys.stdout.write("\t- BibTex (*.tex), --format bibtex\n")
        sys.stdout.write("\t- Text (*.txt), --format text\n")

        # Terminate
        sys.exit(0)

    # Exit if no tools were requested
    tools_to_cite = arguments.tools
    if not tools_to_cite:
        sys.stderr.write(
            "No tools provided for citation! See usage syntax below:\n"
        )
        parser.print_help()
        sys.exit(1)

    # Pass default values if available
    fmt = getattr(arguments, "format")
    output_file = getattr(arguments, "output_file")
    extension = None

    if output_file is None:
        # With no output file, we cannot infer the format from it.
        # So either use the one that was provided if it is supported,
        # or use the default if it was also omitted
        if fmt is not None and fmt not in FORMAT_TO_EXTENSION:
            raise RuntimeError(f"Output format {fmt} is not supported.")
        elif fmt is None:
            # Use default value as this argument was also not provided
            fmt = "text"
    else:
        # Output file provided - resolve path based on OS.
        output_file = Path(output_file)
        extension = output_file.suffix

        # If there was an extension, then infer the format.
        # This will overwrite the fmt argument.
        if extension in EXTENSION_TO_FORMAT:
            fmt = EXTENSION_TO_FORMAT[extension]
        elif not extension:
            if fmt is None:
                # No extension provided, and no format for the citation
                # provided. Throw error.
                raise RuntimeError(
                    "You have not provided a file extension nor citation "
                    "format to write. You must provide one of these."
                )
            elif fmt not in FORMAT_TO_EXTENSION:
                # Format must be supported to allow writing
                raise RuntimeError(
                    f"{fmt} format is not supported, and your output file "
                    "does not provide an implicit format."
                )
        else:
            # This is an extension that we don't support
            raise RuntimeError(
                f"brainglobe-cite does not support writing {extension} files."
            )

    # Invoke API function
    cite(
        *tools_to_cite,
        format=fmt,
        outfile=output_file,
        cite_software=arguments.software_citations,
        warn_on_unused_info=arguments.warn_unused,
    )
    sys.exit(0)
