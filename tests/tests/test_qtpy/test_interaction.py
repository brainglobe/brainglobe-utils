import pytest
from qtpy.QtWidgets import QGridLayout, QGroupBox

from brainglobe_utils.qtpy.interaction import (
    add_button,
    add_checkbox,
    add_combobox,
    add_float_box,
    add_int_box,
)


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

    # callback function for whenever the current index of the combobox changes
    def callback():
        pass

    # returns tuple of (combobox, combobox_label)
    combobox = add_combobox(
        layout,
        row=0,
        label=label,
        items=items,
        label_stack=label_stack,
        callback=callback,
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


def test_add_checkbox(qtbot, box):
    """
    Smoke tests for add_checkbox for all conditional branches
    """
    qtbot.addWidget(box)
    layout = box.layout()
    label = "A checkbox"
    tooltip = "A useful tooltip"

    checkbox = add_checkbox(
        layout=layout, default=True, label=label, tooltip=tooltip
    )

    assert checkbox is not None
    # layout should contain 2 items: QLabel and QCheckbox
    assert layout.count() == 2
    assert layout.itemAt(0).widget().text() == label
    assert checkbox.toolTip() == tooltip


def test_add_float_box(qtbot, box):
    """
    Smoke tests for add_float_box for all conditional branches
    """
    qtbot.addWidget(box)
    layout = box.layout()
    label = "A float box"
    tooltip = "A useful tooltip"
    default = 0.5
    minimum = 0.0
    maximum = 1.0

    floatbox = add_float_box(
        layout=layout,
        default=default,
        minimum=minimum,
        maximum=maximum,
        label=label,
        step=0.1,
        tooltip=tooltip,
    )

    assert floatbox is not None
    # layout should contain 2 items: QLabel and QDoubleSpinBox
    assert layout.count() == 2
    assert layout.itemAt(0).widget().text() == label
    assert floatbox.maximum() == maximum
    assert floatbox.minimum() == minimum
    assert floatbox.value() == default
    assert floatbox.toolTip() == tooltip


def test_add_int_box(qtbot, box):
    """
    Smoke tests for add_float_box for all conditional branches
    """
    qtbot.addWidget(box)
    layout = box.layout()
    label = "An int box"
    tooltip = "A useful tooltip"
    default = 5
    minimum = 0
    maximum = 10

    intbox = add_int_box(
        layout=layout,
        default=default,
        minimum=minimum,
        maximum=maximum,
        label=label,
        tooltip=tooltip,
    )

    assert intbox is not None
    # layout should contain 2 items: QLabel and QSpinBox
    assert layout.count() == 2
    assert layout.itemAt(0).widget().text() == label
    assert intbox.maximum() == maximum
    assert intbox.minimum() == minimum
    assert intbox.value() == default
    assert intbox.toolTip() == tooltip
