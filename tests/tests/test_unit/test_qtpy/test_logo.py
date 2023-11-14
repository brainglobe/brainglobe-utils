from brainglobe_utils.qtpy.logo import header_widget


def test_logo(qtbot):
    package_name = "test"
    package_tagline = "Tagline"
    package_tutorial = "test.html"

    header = header_widget(package_name, package_tagline, package_tutorial)

    qtbot.addWidget(header)

    expected_strings_logo = [package_name, "brainglobe.png"]
    expected_strings_docs = [
        package_tagline,
        package_tutorial,
        "https://brainglobe.info",
        "https://github.com",
    ]

    assert header.layout().count() == 2

    for logo_string in expected_strings_logo:
        assert logo_string in header.layout().itemAt(0).widget().text()

    for docs_string in expected_strings_docs:
        assert docs_string in header.layout().itemAt(1).widget().text()
