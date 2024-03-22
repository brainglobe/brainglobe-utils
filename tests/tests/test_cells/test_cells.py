import os

import pandas as pd
import pytest
from natsort import natsorted

from brainglobe_utils.cells import cells
from brainglobe_utils.IO.cells import get_cells


@pytest.fixture
def cubes_dir(data_path):
    return str(data_path / "cube_extract" / "cubes")


@pytest.fixture
def xml_path(data_path):
    return str(data_path / "cells" / "cells.xml")


@pytest.fixture
def z_planes_validate(data_path):
    csv_path = data_path / "cells" / "z_planes_validate.csv"
    df = pd.read_csv(csv_path, header=None)
    return df.to_numpy().flatten().tolist()


@pytest.fixture
def cell_numbers_in_groups_validate(data_path):
    csv_path = data_path / "cells" / "cell_numbers_in_groups_validate.csv"
    df = pd.read_csv(csv_path, header=None)
    return df.to_numpy().flatten().tolist()


def test_pos_from_file_name(cubes_dir):
    """
    Test that [x, y, z] positions can be extracted from filenames
    """
    positions_validate = [
        [392, 522, 10],
        [340, 1004, 15],
        [340, 1004, 15],
        [392, 522, 10],
    ]
    cube_files = os.listdir(cubes_dir)
    positions = []
    for file in cube_files:
        positions.append(cells.pos_from_file_name(file))
    assert natsorted(positions) == natsorted(positions_validate)


def test_group_cells_by_z(
    xml_path, z_planes_validate, cell_numbers_in_groups_validate
):
    """
    Test that a list of cells can be grouped by z plane
    """
    cell_list = get_cells(xml_path)
    cells_groups = cells.group_cells_by_z(cell_list)
    z_planes_test = list(cells_groups.keys())
    z_planes_test.sort()

    assert z_planes_validate == z_planes_test

    cell_numbers_in_groups_test = [
        len(cells_groups[plane]) for plane in z_planes_test
    ]
    assert cell_numbers_in_groups_validate == cell_numbers_in_groups_test
