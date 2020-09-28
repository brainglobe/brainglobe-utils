import os
import numpy as np
from math import isclose

from imlib.cells.utils import get_cell_location_array

data_dir = os.path.join("tests", "data")
xml_path = os.path.join(data_dir, "cells", "cells_two_types.xml")


def test_get_cell_location_array():
    cell_array = get_cell_location_array(xml_path)
    assert cell_array.shape == (827, 3)
    assert (cell_array[0, :] == np.array([679, 80, 660])).all()

    # cells only
    cell_array = get_cell_location_array(xml_path, cells_only=True)
    assert cell_array.shape == (787, 3)

    # scaling w rounding
    cell_array = get_cell_location_array(
        xml_path, cell_position_scaling=[0.10, 10.1, 101]
    )
    assert (cell_array[0, :] == np.array([68, 808, 66660])).all()

    # scaling w- rounding
    cell_array = get_cell_location_array(
        xml_path, cell_position_scaling=[0.101, 10.1, 101], integer=False
    )
    assert isclose(
        cell_array[0, 0],
        68.579,
        abs_tol=0.01,
    )
    assert isclose(
        cell_array[0, 1],
        808,
        abs_tol=0.01,
    )
    assert isclose(
        cell_array[0, 2],
        66660,
        abs_tol=0.01,
    )
