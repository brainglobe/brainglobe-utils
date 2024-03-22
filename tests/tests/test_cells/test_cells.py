import math
import os

import numpy as np
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


@pytest.mark.parametrize(
    "cell_type, int_type",
    [
        ("cell", cells.Cell.CELL),
        ("no_cell", cells.Cell.ARTIFACT),
        (None, cells.Cell.UNKNOWN),
    ],
    ids=["cell string", "no_cell string", "None"],
)
def test_cell_type(cell_type, int_type):
    """
    Test that creating a cell using a string or None for cell_type creates
    the correct .type
    """
    cell = cells.Cell([1, 1, 1], cell_type)
    assert cell.type == int_type


def test_nan_cell_position():
    """
    Test that nan cell position is replaced with 1.
    """
    cell = cells.Cell([math.nan, 1, np.nan], cells.Cell.CELL)
    assert (cell.x, cell.y, cell.z) == (1, 1, 1)


@pytest.mark.parametrize(
    (
        "x_scale, y_scale, z_scale, x_offset, y_offset, z_offset, integer, "
        "expected"
    ),
    [
        (2.5, 3.5, 4.5, 5.5, 6.5, 7.5, False, [16.25, 26.25, 38.25]),
        (2.5, 3.5, 4.5, 5.5, 6.5, 7.5, True, [16, 26, 38]),
    ],
    ids=["float", "integer"],
)
def test_cell_transform(
    x_scale, y_scale, z_scale, x_offset, y_offset, z_offset, integer, expected
):
    """
    Test that a cell's xyz position can be scaled and offset correctly (with or
    without rounding to nearest integer)
    """
    start_position = [1, 1, 1]
    cell = cells.Cell(start_position, cells.Cell.CELL)

    assert start_position == [cell.x, cell.y, cell.z]

    cell.transform(
        x_scale, y_scale, z_scale, x_offset, y_offset, z_offset, integer
    )

    assert expected == [cell.x, cell.y, cell.z]


@pytest.mark.parametrize(
    (
        "x_scale, y_scale, z_scale, x_offset, y_offset, z_offset, integer, "
        "expected"
    ),
    [
        (2.5, 3.5, 4.5, 5.5, 6.5, 7.5, False, [16.25, 26.25, 38.25]),
        (2.5, 3.5, 4.5, 5.5, 6.5, 7.5, True, [16, 26, 38]),
    ],
    ids=["float", "integer"],
)
def test_cell_soft_transform(
    x_scale, y_scale, z_scale, x_offset, y_offset, z_offset, integer, expected
):
    """
    Test that a cell's position can be scaled and offset correctly using soft
    transform (with or without rounding to nearest integer). This updates
    .transformed_x, .transformed_y and .transformed_z rather than .x, .y and .z
    """
    start_position = [1, 1, 1]
    cell = cells.Cell(start_position, cells.Cell.CELL)

    assert start_position == [cell.x, cell.y, cell.z]

    cell.soft_transform(
        x_scale, y_scale, z_scale, x_offset, y_offset, z_offset, integer
    )

    assert expected == [
        cell.transformed_x,
        cell.transformed_y,
        cell.transformed_z,
    ]
    assert start_position == [cell.x, cell.y, cell.z]


def test_cell_flip_xy():
    """
    Test that a cell's x and y coordinate can be swapped
    """
    start_position = [1, 2, 3]
    cell = cells.Cell(start_position, cells.Cell.CELL)
    assert start_position == [cell.x, cell.y, cell.z]

    cell.flip_x_y()
    assert cell.x == start_position[1]
    assert cell.y == start_position[0]
    assert cell.z == start_position[2]


def test_cell_string_output():
    """
    Test conversion of Cell to string.
    """
    start_pos = [2, 3, 4]
    cell_type = 2
    cell = cells.Cell(start_pos, cell_type)

    assert str(cell) == "Cell: x: 2, y: 3, z: 4, type: 2"

    assert (
        repr(cell)
        == "<class 'brainglobe_utils.cells.cells.Cell'>, ([2, 3, 4], 2)"
    )


def test_untyped_cell():
    """
    Test that an untyped cell can be created, and the type cannot be changed.
    """
    cell = cells.UntypedCell([2, 3, 4])
    assert cell.type == cells.Cell.UNKNOWN

    # Check cell type can't be changed from unknown
    cell.type = cells.Cell.CELL
    assert cell.type == cells.Cell.UNKNOWN


def test_conversion_typed_and_untyped_cell():
    """
    Test conversion in both directions between a typed and untyped cell.
    """
    start_pos = [2, 3, 4]
    untyped_cell = cells.UntypedCell(start_pos)
    typed_cell = cells.Cell(start_pos, cells.Cell.UNKNOWN)

    assert cells.UntypedCell.from_cell(typed_cell) == untyped_cell
    assert untyped_cell.to_cell() == typed_cell
