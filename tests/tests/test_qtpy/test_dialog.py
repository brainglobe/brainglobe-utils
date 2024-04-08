import pytest
from qtpy.QtWidgets import QGroupBox, QMessageBox

from brainglobe_utils.qtpy.dialog import display_warning


@pytest.mark.parametrize(
    "messagebox_return",
    [QMessageBox.Yes, QMessageBox.Cancel],
    ids=["Yes", "Cancel"],
)
def test_display_warning(qtbot, monkeypatch, messagebox_return):
    """
    Test display_warning returns True/False when accepted/cancelled.
    """
    # Use monkeypatch to return a set value from the modal dialog.
    monkeypatch.setattr(
        QMessageBox, "question", lambda *args: messagebox_return
    )

    box = QGroupBox()
    qtbot.addWidget(box)
    response = display_warning(box, "warning", "an example message")
    if messagebox_return == QMessageBox.Yes:
        assert response is True
    else:
        assert response is False
