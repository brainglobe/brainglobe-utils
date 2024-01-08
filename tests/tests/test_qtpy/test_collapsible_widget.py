import pytest
from qtpy.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from brainglobe_utils.qtpy.collapsible_widget import (
    CollapsibleWidget,
    CollapsibleWidgetContainer,
)

WIDGET_TITLE = "Title"


@pytest.fixture(scope="class")
def generic_widget() -> QWidget:
    widget = QWidget()
    return widget


@pytest.fixture(scope="class")
def collapsible_widget() -> CollapsibleWidget:
    collapsible_widget = CollapsibleWidget(WIDGET_TITLE)
    return collapsible_widget


@pytest.fixture(scope="class")
def collapsible_widget_container() -> CollapsibleWidgetContainer:
    collapsible_widget_container = CollapsibleWidgetContainer()
    return collapsible_widget_container


def test_collapsible_widget_empty(qtbot, collapsible_widget):
    qtbot.addWidget(collapsible_widget)

    assert collapsible_widget.text() == WIDGET_TITLE
    assert not collapsible_widget.isExpanded()
    assert collapsible_widget.content().layout().count() == 0


def test_collapsible_widget_filled(qtbot, collapsible_widget):
    label_str = "test"
    collapsible_widget.addWidget(QPushButton(label_str))

    qtbot.addWidget(collapsible_widget)

    assert collapsible_widget.content().layout().count() == 1


def test_collapsible_widget_click_once(qtbot, collapsible_widget):
    qtbot.addWidget(collapsible_widget)

    with qtbot.waitSignal(
        collapsible_widget.toggled_signal_with_self, timeout=1000
    ) as blocker:
        collapsible_widget._toggle_btn.click()

    assert blocker.args == [collapsible_widget, True]


@pytest.mark.parametrize("num_clicks", [2, 5, 100])
def test_collapsible_widget_click_multiple(
    qtbot, collapsible_widget, num_clicks
):
    """
    Test that the toggled_signal_with_self signal is emitted the correct
    number of times and with the correct parameters when clicked multiple
    times.
    """
    qtbot.addWidget(collapsible_widget)

    current_state = collapsible_widget.isExpanded()

    # Function to check the signal is emitted with the correct parameters
    # The signaller should be the collapsible widget and the state should
    # match the state tracked manually in current_state
    def check_signal_valid(signaller, state):
        return signaller == collapsible_widget and state == current_state

    with qtbot.waitSignals(
        [collapsible_widget.toggled_signal_with_self] * num_clicks,
        check_params_cbs=[check_signal_valid] * num_clicks,
        timeout=1000,
    ):
        for _ in range(num_clicks + 1):
            # Invert the current state to simulate a toggle manually
            current_state = not current_state
            collapsible_widget._toggle_btn.click()


def test_collapsible_widget_container(qtbot, collapsible_widget_container):
    qtbot.addWidget(collapsible_widget_container)

    assert collapsible_widget_container.layout().count() == 0
    assert len(collapsible_widget_container.collapsible_widgets) == 0


@pytest.mark.parametrize(
    "layout", [QVBoxLayout(), QHBoxLayout(), QFormLayout()]
)
def test_collapsible_widget_container_add_collapsible_widget(
    qtbot, collapsible_widget_container, generic_widget, layout
):
    qtbot.addWidget(collapsible_widget_container)

    generic_widget.setLayout(layout)
    generic_widget.layout().addWidget(QLabel("test"))
    generic_widget.layout().addWidget(QPushButton("test"))

    collapsible_widget_container.add_widget(
        generic_widget, collapsible=True, widget_title=WIDGET_TITLE
    )

    # Check that the widget was added and is a CollapsibleWidget
    assert collapsible_widget_container.layout().count() == 1
    assert isinstance(
        collapsible_widget_container.layout().itemAt(0).widget(),
        CollapsibleWidget,
    )
    # Check that the widget is collapsed and contains the generic widget
    assert (
        collapsible_widget_container.collapsible_widgets[0].content()
        is generic_widget
    )
    assert (
        collapsible_widget_container.layout().itemAt(0).widget().text()
        == WIDGET_TITLE
    )
    assert (
        not collapsible_widget_container.layout()
        .itemAt(0)
        .widget()
        .isExpanded()
    )
    assert len(collapsible_widget_container.collapsible_widgets) == 1


@pytest.mark.parametrize("widget_type", [QLabel, QPushButton])
def test_collapsible_widget_container_add_not_collapsible_widget(
    qtbot, collapsible_widget_container, widget_type
):
    qtbot.addWidget(collapsible_widget_container)

    collapsible_widget_container.add_widget(
        widget_type(WIDGET_TITLE), collapsible=False
    )

    assert collapsible_widget_container.layout().count() == 1
    assert isinstance(
        collapsible_widget_container.layout().itemAt(0).widget(), widget_type
    )
    assert len(collapsible_widget_container.collapsible_widgets) == 0


@pytest.mark.parametrize(
    "layout, collapsible",
    [
        (QVBoxLayout(), True),
        (QHBoxLayout(), True),
        (QFormLayout(), True),
        (QVBoxLayout(), False),
        (QHBoxLayout(), False),
        (QFormLayout(), False),
    ],
)
def test_collapsible_widget_container_add_remove_widgets(
    qtbot, collapsible_widget_container, generic_widget, layout, collapsible
):
    qtbot.addWidget(collapsible_widget_container)

    generic_widget.setLayout(layout)
    generic_widget.layout().addWidget(QLabel("test"))
    generic_widget.layout().addWidget(QPushButton("test"))

    collapsible_widget_container.add_widget(
        generic_widget, collapsible=collapsible, widget_title=WIDGET_TITLE
    )

    assert collapsible_widget_container.layout().count() == 1
    # Convert collapsible to int (False -> 0, True -> 1)
    # to check if collapsible_widgets is empty
    assert len(collapsible_widget_container.collapsible_widgets) == int(
        collapsible
    )

    collapsible_widget_container.remove_widget(generic_widget)

    assert collapsible_widget_container.layout().count() == 0
    assert len(collapsible_widget_container.collapsible_widgets) == 0


def test_collapsible_widget_container_add_remove_diff_widgets(
    qtbot, generic_widget, collapsible_widget_container
):
    qtbot.addWidget(collapsible_widget_container)
    other_widget = QLabel("test")

    collapsible_widget_container.add_widget(
        generic_widget, collapsible=True, widget_title=WIDGET_TITLE
    )
    collapsible_widget_container.add_widget(other_widget, collapsible=False)

    assert collapsible_widget_container.layout().count() == 2
    assert len(collapsible_widget_container.collapsible_widgets) == 1

    collapsible_widget_container.remove_widget(generic_widget)

    assert collapsible_widget_container.layout().count() == 1
    assert len(collapsible_widget_container.collapsible_widgets) == 0

    collapsible_widget_container.remove_widget(other_widget)

    assert collapsible_widget_container.layout().count() == 0
    assert len(collapsible_widget_container.collapsible_widgets) == 0


def test_collapsible_widget_container_remove_widget_not_found(
    qtbot, generic_widget, collapsible_widget_container
):
    with pytest.raises(ValueError):
        collapsible_widget_container.remove_widget(generic_widget)


@pytest.mark.parametrize(
    "num_collapsible_widgets, num_other_widgets, index_expanded",
    [(2, 4, 1), (5, 1, 3), (10, 0, 9)],
)
def test_collapsible_widget_container_update_drawers(
    qtbot,
    collapsible_widget_container,
    num_collapsible_widgets,
    num_other_widgets,
    index_expanded,
):
    """
    Test that the collapsible widgets in the container are expanded/collapsed
    correctly when the _update_drawers function is called.

    A container is created with num_collapsible_widgets collapsible widgets
    and num_other_widgets other widgets. The index_expanded collapsible widget
    is expanded and the state of each widget is checked. index_expanded is
    then incremented (modulo num_collapsible_widgets) to simulate toggling
    each collapsible widget in sequence. Checks the state of each widget after
    every iteration.
    """
    qtbot.addWidget(collapsible_widget_container)
    collapsible_widgets = []
    non_collapsible_widgets = []

    # Add collapsible widgets and other widgets to the container alternating
    # until the correct number of each type of widget has been added
    for i in range(num_collapsible_widgets + num_other_widgets):
        if i % 2 == 0 and len(non_collapsible_widgets) < num_other_widgets:
            collapsible_widget_container.add_widget(
                QLabel("test"), collapsible=False
            )
            non_collapsible_widgets.append(
                collapsible_widget_container.layout().itemAt(i).widget()
            )
        elif len(collapsible_widgets) < num_collapsible_widgets:
            collapsible_widget_container.add_widget(
                QLabel("test"), collapsible=True
            )
            collapsible_widgets.append(
                collapsible_widget_container.layout().itemAt(i).widget()
            )
        else:
            collapsible_widget_container.add_widget(
                QLabel("test"), collapsible=False
            )
            non_collapsible_widgets.append(
                collapsible_widget_container.layout().itemAt(i).widget()
            )

    for _ in range(num_collapsible_widgets):
        collapsible_widgets[index_expanded]._toggle_btn.click()

        for i in range(num_collapsible_widgets):
            assert collapsible_widgets[i].isExpanded() == (i == index_expanded)

        for widget in non_collapsible_widgets:
            assert not widget.isHidden()

        index_expanded = (index_expanded + 1) % num_collapsible_widgets
