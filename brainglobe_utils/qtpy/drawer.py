from qtpy.QtCore import Qt, Signal
from qtpy.QtWidgets import QPushButton, QVBoxLayout, QWidget


class Drawer(QWidget):
    """
    LayerList class which acts as collapsable list.
    """

    toggled_signal = Signal(QWidget, bool)

    def __init__(self, name, expand=False):
        super().__init__()
        self.currently_expanded = expand
        self.main_layout = QVBoxLayout()

        self.expand_button = QPushButton(name)
        self.expand_button.setToolTip(f"{name}")

        # self.expand_button.setIcon \
        # (QIcon(os.path.join(PATH, 'LayersList_Up.png')))

        self.main_layout.addWidget(self.expand_button, 0, Qt.AlignTop)

        self.expand_button.clicked.connect(self._on_expand_toggle)
        self.setLayout(self.main_layout)

    def _on_expand_toggle(self):
        self.toggle_expansion()
        self.toggled_signal.emit(self, self.currently_expanded)

    def toggle_expansion(self):
        self.currently_expanded = not self.currently_expanded
        for i in range(1, self.layout().count()):
            self.layout().itemAt(i).widget().setVisible(
                self.currently_expanded
            )

    def add(self, widget: QWidget):
        widget.setVisible(False)
        self.layout().addWidget(widget)
