from typing import List, Optional

from qtpy.QtCore import Qt, Signal
from qtpy.QtWidgets import QVBoxLayout, QWidget
from superqt.collapsible import QCollapsible


class CollapsibleWidget(QCollapsible):
    """
    Custom collapsible widget.

    Attributes
    ----------
    toggled_signal_with_self : Signal
        Emitted when the CollapsibleWidget is toggled.
        Provides the CollapsibleWidget instance and the new state.

    Parameters
    ----------
    title : str, optional
        The title of the CollapsibleWidget.
    parent : QWidget or None, optional
        The parent widget.
    """

    toggled_signal_with_self = Signal(QCollapsible, bool)

    def __init__(
        self,
        title: str = "",
        parent: Optional[QWidget] = None,
        expanded_icon: Optional[str] = "▼",
        collapsed_icon: Optional[str] = "▶",
    ):
        """
        Initializes a new CollapsibleWidget instance.

        Parameters
        ----------
        title : str, optional
            The title of the CollapsibleWidget.
        parent : QWidget or None, optional
            The parent widget.
        """
        super().__init__(
            title,
            parent,
            expandedIcon=expanded_icon,
            collapsedIcon=collapsed_icon,
        )
        self.currently_expanded = False

        self.toggled.connect(self._on_toggle)

    def _on_toggle(self, state):
        """
        Handles the toggled signal by emitting the custom signal
         with the CollapsibleWidget instance and the new state.

        Parameters
        ----------
        state : bool
            The new state of the CollapsibleWidget
            (True if expanded, False if collapsed).
        """
        self.toggled_signal_with_self.emit(self, state)


class CollapsibleWidgetContainer(QWidget):
    """
    Container for multiple CollapsibleWidgets with the ability to add,
    remove, and synchronize their states. Non-CollapsibleWidgets can also
    be added.

    Methods
    -------
    add_widget(QWidget)
        Adds a widget to the CollapsibleWidgetContainer.
    remove_drawer(QWidget or CollapsibleWidget)
        Removes a widget from the CollapsibleWidgetContainer.
    _update_drawers(signalling_drawer, state)
        Private method to synchronize drawer states.
    """

    def __init__(self, parent=None):
        """
        Initializes a new CollapsibleWidgetContainer instance.
        """
        super().__init__(parent)
        self.setLayout(QVBoxLayout())

        self.layout().setAlignment(Qt.AlignTop)
        self.layout().setSpacing(0)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.collapsible_widgets: List[CollapsibleWidget] = []

    def add_widget(
        self, widget: QWidget, collapsible: bool = True, widget_title: str = ""
    ):
        """
        Adds a QWidget or a CollapsibleWidget to the chest.

        Parameters
        ----------
        widget : QWidget
            The widget instance to be added.
        collapsible : bool, optional
            Whether the widget should be collapsible.
        widget_title : str, optional
            The title of the widget.
        """
        if collapsible:
            collapsible_widget = CollapsibleWidget(widget_title, parent=self)
            collapsible_widget.setContent(widget)
            collapsible_widget.toggled_signal_with_self.connect(
                self._update_drawers
            )
            collapsible_widget.collapse(animate=False)
            self.collapsible_widgets.append(collapsible_widget)
            self.layout().addWidget(collapsible_widget, 0, Qt.AlignTop)
        else:
            self.layout().addWidget(widget, 0, Qt.AlignTop)

    def remove_widget(self, widget: QWidget):
        """
        Removes a widget from the chest.

        Parameters
        ----------
        widget : QWidget
            The widget instance to be removed.

        Raises
        ------
        ValueError
            If the widget is not found.
        """
        for i in range(self.layout().count()):
            child_widget = self.layout().itemAt(i).widget()
            if (
                isinstance(child_widget, CollapsibleWidget)
                and child_widget.content() is widget
            ):
                self.layout().removeWidget(child_widget)
                self.collapsible_widgets.remove(child_widget)
                child_widget.toggled_signal_with_self.disconnect(
                    self._update_drawers
                )
                return
            elif child_widget is widget:
                self.layout().removeWidget(widget)
                return

        raise ValueError("Widget not found")

    def _update_drawers(
        self, signalling_widget: CollapsibleWidget, state: bool
    ):
        """
        Synchronizes CollapsibleWidget states to ensure only one
        CollapsibleWidget is expanded at a time.

        Parameters
        ----------
        signalling_widget : CollapsibleWidget
            The CollapsibleWidget emitting the signal.
        state : bool
            The new state of the signalling_widget.
        """
        if state:
            for collapsible_widget in self.collapsible_widgets:
                if collapsible_widget is not signalling_widget:
                    collapsible_widget.collapse(False)
