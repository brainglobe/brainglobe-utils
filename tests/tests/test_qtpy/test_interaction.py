import pytest
from qtpy.QtWidgets import QGridLayout

from brainglobe_utils.qtpy.interaction import add_button, add_combobox


@pytest.mark.parametrize("label_stack", [True, False])
@pytest.mark.parametrize("label", ["A label", None])
def test_add_combobox(label, label_stack):
    """
    Smoke test for add_combobox for all conditional branches
    """
    layout = QGridLayout()
    combobox = add_combobox(
        layout,
        row=0,
        label=label,
        items=["item 1", "item 2"],
        label_stack=label_stack,
    )
    assert combobox is not None


@pytest.mark.parametrize(
    argnames="alignment", argvalues=["center", "left", "right"]
)
def test_add_button(alignment):
    """
    Smoke tests for add_button for all conditional branches
    """
    layout = QGridLayout()
    button = add_button(
        layout=layout,
        connected_function=lambda: None,
        label="A button",
        row=0,
        alignment=alignment,
    )
    assert button is not None
