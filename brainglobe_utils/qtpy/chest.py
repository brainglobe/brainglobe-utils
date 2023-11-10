from qtpy.QtCore import Qt
from qtpy.QtWidgets import QGroupBox, QVBoxLayout


class Chest(QGroupBox):
    def __init__(self):
        super().__init__()
        self.setLayout(QVBoxLayout())

        self.layout().setAlignment(Qt.AlignTop)
        self.layout().setSpacing(0)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.drawers = []

    def add_drawer(self, drawer):
        self.drawers.append(drawer)
        self.layout().addWidget(drawer, 0, Qt.AlignTop)
        drawer.toggled_signal.connect(self._update_drawers)

    def _update_drawers(self, signalling_drawer, state):
        if state:
            for drawer in self.drawers:
                if (
                    drawer is not signalling_drawer
                    and drawer.currently_expanded
                ):
                    drawer.toggle_expansion()
