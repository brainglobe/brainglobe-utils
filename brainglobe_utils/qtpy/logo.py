from importlib.resources import files
from typing import Optional

from qtpy.QtWidgets import QGroupBox, QHBoxLayout, QLabel, QWidget


def _docs_links_widget(
    package_name: str,
    package_tagline: str,
    tutorial_file_name: Optional[str] = None,
    documentation_path: Optional[str] = None,
    citation_doi: Optional[str] = None,
    github_repo_name: Optional[str] = None,
    help_text: Optional[str] = None,
    parent: Optional[QWidget] = None,
):
    lines = [
        "<h3>",
        f"<p>{package_tagline}</p>",
        "<p><a href='https://brainglobe.info' style='color:gray;'>"
        "Website</a></p>",
    ]

    if tutorial_file_name:
        lines.append(
            f"<p>"
            f"<a href='https://brainglobe.info/tutorials/{tutorial_file_name}'"
            f" style='color:gray;'>Tutorial</a></p>"
        )

    if documentation_path:
        lines.append(
            f"<p><a href="
            f"'https://brainglobe.info/documentation/{documentation_path}' "
            f"style='color:gray;'>Documentation</a></p>"
        )

    if github_repo_name is None:
        github_repo_name = package_name
    lines.append(
        f"<p><a href='https://github.com/brainglobe/{github_repo_name}' "
        f"style='color:gray;'>Source</a></p>"
    )

    if citation_doi:
        lines.append(
            f"<p><a href='{citation_doi}' style='color:gray;'>Citation</a></p>"
        )

    if help_text:
        lines.append(f"<p><small>{help_text}</small></p>")

    lines.append("</h3>")
    docs_links_widget = QLabel("\n".join(lines), parent=parent)
    docs_links_widget.setOpenExternalLinks(True)
    return docs_links_widget


def _logo_widget(package_name: str, parent: Optional[QWidget] = None):
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
    tutorial_file_name: Optional[str] = None,
    documentation_path: Optional[str] = None,
    citation_doi: Optional[str] = None,
    github_repo_name: Optional[str] = None,
    help_text: Optional[str] = None,
    parent: Optional[QWidget] = None,
) -> QGroupBox:
    """
    Render HTML in a QGroupBox with a BrainGlobe logo and links to the docs
     and source code.

    Parameters
    ----------
    package_name : str
        The name of the package, e.g. "brainrender-napari"
    package_tagline : str
        The tagline for the package
    tutorial_file_name : str, optional
        The name of the tutorial file (must include .html),
         e.g. "brainrender-qtpy.html"
    documentation_path : str, optional
        Path of documentation file relative to
        https://brainglobe.info/documentation/ (must include .html),
        e.g. "cellfinder/user-guide/napari-plugin/index.html"
    citation_doi : str, optional
        Doi of citation e.g. "https://doi.org/10.1371/journal.pcbi.1009074"
    github_repo_name : str, optional
        Name of github repository inside the BrainGlobe organisation
        (https://github.com/brainglobe). Only necessary if the github
        repository name isn't the same as the package name.
    help_text : str, optional
        Help text to display at the bottom or the header e.g.
        "For help, hover the cursor over each parameter."
    parent : QWidget, optional
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
            package_name,
            package_tagline,
            tutorial_file_name,
            documentation_path,
            citation_doi,
            github_repo_name,
            help_text,
            parent=box,
        )
    )

    return box
