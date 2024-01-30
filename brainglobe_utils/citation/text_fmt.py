from brainglobe_utils.citation.format import Format


class TextCitation(Format):
    """
    Generates a reference string that can be copy-pasted into a
    text document's bibliography for use as a reference.

    Style of text-based references will be

    <citation-sentence>;
    <authors> (<year>). <title>.
    <journal>, <volume>(<issue>), <doi>, <url>

    Required information:
    - authors
    - title
    - year

    Optional information:
    - citation-sentence
    - journal
    - volume
    - issue
    - doi
    - url
    """

    required = ["authors", "title", "year"]
    optional = [
        "citation-sentence",
        "journal",
        "volume",
        "issue",
        "issn",
        "doi",
        "url",
    ]

    def generate_ref_string(self) -> str:
        """
        Generate a string that encodes the reference, in preparation for
        writing to an output format.
        """
        output_string = ""

        # Include optional sentence if provided
        if getattr(self, "citation_sentence") is not None:
            output_string += f"{getattr(self, 'citation_sentence')};\n"

        # Required fields
        output_string += f"{getattr(self, 'authors')} "
        output_string += f"({getattr(self, 'year')}). "
        output_string += f"{getattr(self, 'title')}.\n"

        # Optional information on final line
        if getattr(self, "journal") is not None:
            output_string += f"{getattr(self, 'journal')}, "
        if getattr(self, "volume") is not None:
            output_string += f"{getattr(self, 'volume')}"
            if getattr(self, "issn") is not None:
                output_string += f"({getattr(self, 'issn')}), "
            elif getattr(self, "issue") is not None:
                output_string += f"({getattr(self, 'issue')}), "
        if getattr(self, "doi") is not None:
            output_string += f"{getattr(self, 'doi')}, "
        if getattr(self, "url") is not None:
            output_string += f"{getattr(self, 'url')}, "

        # Trim hanging comma if present
        output_string = output_string.strip()
        output_string = output_string.strip(",")

        return output_string
