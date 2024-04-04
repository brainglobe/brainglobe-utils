from typing import Callable, List, Optional, Tuple

from qtpy.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QLabel,
    QLayout,
    QPushButton,
    QSpinBox,
)


def add_button(
    label: str,
    layout: QLayout,
    connected_function: Callable,
    *,
    row: int = 0,
    column: int = 0,
    visibility: bool = True,
    minimum_width: int = 0,
    alignment: str = "center",
    tooltip: Optional[str] = None,
) -> QPushButton:
    """
    Add a button to *layout*.
    """
    button = QPushButton(label)
    if alignment == "center":
        pass
    elif alignment == "left":
        button.setStyleSheet("QPushButton { text-align: left; }")
    elif alignment == "right":
        button.setStyleSheet("QPushButton { text-align: right; }")

    button.setVisible(visibility)
    button.setMinimumWidth(minimum_width)

    if tooltip:
        button.setToolTip(tooltip)

    layout.addWidget(button, row, column)
    button.clicked.connect(connected_function)
    return button


def add_checkbox(
    layout: QLayout,
    default: bool,
    label: str,
    row: int = 0,
    column: int = 0,
    tooltip: Optional[str] = None,
) -> QCheckBox:
    """
    Add a checkbox to *layout*.
    """
    box = QCheckBox()
    box.setChecked(default)
    if tooltip:
        box.setToolTip(tooltip)
    layout.addWidget(QLabel(label), row, column)
    layout.addWidget(box, row, column + 1)
    return box


def add_float_box(
    layout: QLayout,
    default: float,
    minimum: float,
    maximum: float,
    label: str,
    step: float,
    row: int = 0,
    column: int = 0,
    tooltip: Optional[str] = None,
) -> QDoubleSpinBox:
    """
    Add a spin box for float values to *layout*.
    """
    box = QDoubleSpinBox()
    box.setMinimum(minimum)
    box.setMaximum(maximum)
    box.setValue(default)
    box.setSingleStep(step)
    if tooltip:
        box.setToolTip(tooltip)
    layout.addWidget(QLabel(label), row, column)
    layout.addWidget(box, row, column + 1)
    return box


def add_int_box(
    layout: QLayout,
    default: int,
    minimum: int,
    maximum: int,
    label: str,
    row: int = 0,
    column: int = 0,
    tooltip: Optional[str] = None,
) -> QSpinBox:
    """
    Add a spin box for integer values to *layout*.
    """
    box = QSpinBox()
    box.setMinimum(minimum)
    box.setMaximum(maximum)
    # Not always set if not after min & max
    box.setValue(default)
    if tooltip:
        box.setToolTip(tooltip)
    layout.addWidget(QLabel(label), row, column)
    layout.addWidget(box, row, column + 1)
    return box


def add_combobox(
    layout: QLayout,
    label: str,
    items: List[str],
    row: int = 0,
    column: int = 0,
    label_stack: bool = False,
    callback=None,
    width: int = 150,
) -> Tuple[QComboBox, Optional[QLabel]]:
    """
    Add a selection box to *layout*.
    """
    if label_stack:
        combobox_row = row + 1
        combobox_column = column
    else:
        combobox_row = row
        combobox_column = column + 1
    combobox = QComboBox()
    combobox.addItems(items)
    if callback:
        combobox.currentIndexChanged.connect(callback)
    combobox.setMaximumWidth = width

    if label is not None:
        combobox_label = QLabel(label)
        combobox_label.setMaximumWidth = width
        layout.addWidget(combobox_label, row, column)
    else:
        combobox_label = None

    layout.addWidget(combobox, combobox_row, combobox_column)
    return combobox, combobox_label
