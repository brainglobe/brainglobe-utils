import pytest
from qtpy.QtWidgets import QGridLayout, QGroupBox

from brainglobe_utils.qtpy.interaction import add_button, add_combobox


@pytest.fixture()
def box() -> QGroupBox:
    """
    Return a QGroupBox with a grid layout.
    """
    box = QGroupBox()
    layout = QGridLayout()
    box.setLayout(layout)

    return box


@pytest.mark.parametrize("label_stack", [True, False])
@pytest.mark.parametrize("label", ["A label", None])
def test_add_combobox(qtbot, box, label, label_stack):
    """
    Smoke test for add_combobox for all conditional branches
    """
    qtbot.addWidget(box)
    layout = box.layout()
    items = ["item 1", "item 2"]

    # returns tuple of (combobox, combobox_label)
    combobox = add_combobox(
        layout,
        row=0,
        label=label,
        items=items,
        label_stack=label_stack,
    )

    assert combobox is not None
    assert combobox[0].count() == len(items)

    if label is None:
        assert combobox[1] is None
        assert layout.count() == 1
    else:
        assert combobox[1].text() == label
        assert layout.count() == 2


@pytest.mark.parametrize("alignment", ["center", "left", "right"])
def test_add_button(qtbot, box, alignment):
    """
    Smoke tests for add_button for all conditional branches
    """
    qtbot.addWidget(box)
    layout = box.layout()
    label = "A button"
    tooltip = "A useful tooltip"

    button = add_button(
        layout=layout,
        connected_function=lambda: None,
        label=label,
        row=0,
        alignment=alignment,
        tooltip=tooltip,
    )

    assert button is not None
    assert layout.count() == 1
    assert button.text() == label
    assert button.toolTip() == tooltip
