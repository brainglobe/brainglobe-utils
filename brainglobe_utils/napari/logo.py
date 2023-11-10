from importlib.resources import files

from qtpy.QtWidgets import QGroupBox, QHBoxLayout, QLabel, QWidget


def _docs_links_widget(
    package_name: str, tutorial_file_name: str, parent: QWidget = None
):
    _docs_links_html = f"""
    <h3>
    <p>2D Registration</p>
    <p><a href="https://brainglobe.info" style="color:gray;">Website</a></p>
    <p><a href="https://brainglobe.info/tutorials/{tutorial_file_name}" style="color:gray;">Tutorial</a></p>
    <p><a href="https://github.com/brainglobe/{package_name}" style="color:gray;">Source</a></p>
    </h3>
    """  # noqa: E501
    docs_links_widget = QLabel(_docs_links_html, parent=parent)
    docs_links_widget.setOpenExternalLinks(True)
    return docs_links_widget


def _logo_widget(package_name: str, parent: QWidget = None):
    brainglobe_logo = files("brainglobe.png")

    _logo_html = f"""
    <h1>
    <img src="{brainglobe_logo}"width="100">
    <p>{package_name}</p>
    <\h1>
    """

    return QLabel(_logo_html, parent=None)


def header_widget(
    package_name: str, tutorial_file_name: str, parent: QWidget = None
):
    """
    Render HTML in a QGroupBox with a BrainGlobe logo and links to the docs
     and source code.
    Args:
        package_name: The name of the package, e.g. "brainrender-napari"
        tutorial_file_name: The name of the tutorial file
            (must include .html), e.g. "brainrender-napari.html"
        parent: The parent widget

    Returns: A QGroupBox with the rendered HTML containing the logo and links
    """

    box = QGroupBox(parent)
    box.setFlat(True)
    box.setLayout(QHBoxLayout())
    box.layout().addWidget(_logo_widget(package_name, parent=box))
    box.layout().addWidget(
        _docs_links_widget(package_name, tutorial_file_name, parent=box)
    )

    return box
