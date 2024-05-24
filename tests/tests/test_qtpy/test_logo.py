from brainglobe_utils.qtpy.logo import header_widget


def test_logo(qtbot):
    package_name = "test"
    package_tagline = "Tagline"
    tutorial_file_name = "test-tutorial.html"
    documentation_path = "test-docs/test.html"
    citation_doi = "https://doi.org/test"
    help_text = "For help, hover the cursor over each parameter."

    header = header_widget(
        package_name,
        package_tagline,
        tutorial_file_name=tutorial_file_name,
        documentation_path=documentation_path,
        citation_doi=citation_doi,
        help_text=help_text,
    )

    qtbot.addWidget(header)

    expected_strings_logo = [package_name, "brainglobe.png"]
    expected_strings_docs = [
        package_tagline,
        tutorial_file_name,
        documentation_path,
        citation_doi,
        help_text,
        "https://brainglobe.info",
        "https://github.com",
    ]

    assert header.layout().count() == 2

    for logo_string in expected_strings_logo:
        assert logo_string in header.layout().itemAt(0).widget().text()

    for docs_string in expected_strings_docs:
        assert docs_string in header.layout().itemAt(1).widget().text()


def test_logo_list_of_links(qtbot):
    package_name = "test"
    package_tagline = "Tagline"

    links = {
        "Website": "https://brainglobe.info",
        "Source": "https://github.com",
        "Tutorial": "https://brainglobe.info/tutorials/test.html",
    }

    expected_string = (
        f"<h3>\n<p>{package_tagline}</p>\n"
        f"<p><a href='https://brainglobe.info' style='color:gray;'>"
        f"Website</a></p>\n"
        f"<p><a href='https://github.com' style='color:gray;'>"
        f"Source</a></p>\n"
        f"<p><a href='https://brainglobe.info/tutorials/test.html' "
        f"style='color:gray;'>"
        f"Tutorial</a></p>\n</h3>"
    )

    header = header_widget(package_name, package_tagline, links=links)

    qtbot.addWidget(header)

    # Check that the contents of the links are in the header
    assert expected_string == header.layout().itemAt(1).widget().text()
