from qtpy.QtWidgets import QLabel

from brainglobe_utils.qtpy.chest import Chest
from brainglobe_utils.qtpy.drawer import Drawer


def test_layers_list(qtbot):
    chest = Chest()
    drawer = Drawer("test")
    drawer_2 = Drawer("test2")
    drawer.add(QLabel("test"))
    drawer.add(QLabel("test2"))
    drawer_2.add(QLabel("test"))
    drawer_2.add(QLabel("test2"))

    chest.add_drawer(drawer)
    chest.add_drawer(drawer_2)
    qtbot.addWidget(chest)

    chest.window().show()

    qtbot.wait(100000)
