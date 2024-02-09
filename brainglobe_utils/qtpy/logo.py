from importlib.resources import files

from qtpy.QtWidgets import QGroupBox, QHBoxLayout, QLabel, QWidget


def _docs_links_widget(
    package_name: str,
    package_tagline: str,
    tutorial_file_name: str,
    parent: QWidget = None,
):
    _docs_links_html = f"""
    <h3>
    <p>{package_tagline}</p>
    <p><a href="https://brainglobe.info" style="color:gray;">Website</a></p>
    <p><a href="https://brainglobe.info/tutorials/{tutorial_file_name}" style="color:gray;">Tutorial</a></p>
    <p><a href="https://github.com/brainglobe/{package_name}" style="color:gray;">Source</a></p>
    </h3>
    """  # noqa: E501
    docs_links_widget = QLabel(_docs_links_html, parent=parent)
    docs_links_widget.setOpenExternalLinks(True)
    return docs_links_widget


def _logo_widget(package_name: str, parent: QWidget = None):
    brainglobe_logo = files("brainglobe_utils").joinpath("qtpy/brainglobe.png")

    _logo_html = f"""
    <h1>
    <img src="{brainglobe_logo}"width="100">
    <p>{package_name}</p>
    </h1>
    """  # noqa W605

    return QLabel(_logo_html, parent=None)


def header_widget(
    package_name: str,
    package_tagline: str,
    tutorial_file_name: str,
    parent: QWidget = None,
):
    """
    Render HTML in a QGroupBox with a BrainGlobe logo and links to the docs
     and source code.

    Parameters
    ----------
    package_name : str
        The name of the package, e.g. "brainrender-napari"
    package_tagline : str
        The tagline for the package
    tutorial_file_name : str
        The name of the tutorial file (must include .html),
         e.g. "brainrender-qtpy.html": str
    parent : QWidget
        The parent widget, defaults to None

    Returns
    -------
    QGroupBox
        A QGroupBox with the rendered HTML containing the logo and links
    """

    box = QGroupBox(parent)
    box.setFlat(True)
    box.setLayout(QHBoxLayout())
    box.layout().addWidget(_logo_widget(package_name, parent=box))
    box.layout().addWidget(
        _docs_links_widget(
            package_name, package_tagline, tutorial_file_name, parent=box
        )
    )

    return box
