from typing import List

import numpy as np

from brainglobe_utils.cells.cells import Cell, from_numpy_pos, match_cells


def as_cell(x: List[float]):
    d = np.tile(np.asarray([x]).T, (1, 3))
    cells = from_numpy_pos(d, Cell.UNKNOWN)
    return cells


def test_cell_matches_equal_size():
    a = as_cell([10, 20, 30, 40])
    b = as_cell([5, 15, 25, 35])
    a_, ab, b_ = match_cells(a, b)
    assert not a_
    assert not b_
    assert [[0, 0], [1, 1], [2, 2], [3, 3]] == ab

    a = as_cell([20, 10, 30, 40])
    b = as_cell([5, 15, 25, 35])
    a_, ab, b_ = match_cells(a, b)
    assert not a_
    assert not b_
    assert [[0, 1], [1, 0], [2, 2], [3, 3]] == ab

    a = as_cell([20, 10, 30, 40])
    b = as_cell([11, 22, 39, 42])
    a_, ab, b_ = match_cells(a, b)
    assert not a_
    assert not b_
    assert [[0, 1], [1, 0], [2, 2], [3, 3]] == ab


def test_cell_matches_larger_other():
    a = as_cell([1, 12, 100, 80])
    b = as_cell([5, 15, 25, 35, 100])
    a_, ab, b_ = match_cells(a, b)
    assert not a_
    assert b_ == [2]
    assert [[0, 0], [1, 1], [2, 4], [3, 3]] == ab

    a = as_cell([20, 10, 30, 40])
    b = as_cell([11, 22, 39, 42, 41])
    a_, ab, b_ = match_cells(a, b)
    assert not a_
    assert b_ == [3]
    assert [[0, 1], [1, 0], [2, 2], [3, 4]] == ab


def test_cell_matches_larger_cells():
    a = as_cell([5, 15, 25, 35, 100])
    b = as_cell([1, 12, 100, 80])
    a_, ab, b_ = match_cells(a, b)
    assert a_ == [2]
    assert not b_
    assert [[0, 0], [1, 1], [3, 3], [4, 2]] == ab


def test_cell_matches_threshold():
    a = as_cell([10, 12, 100, 80])
    b = as_cell([0, 5, 15, 25, 35, 100])
    a_, ab, b_ = match_cells(a, b)
    assert not a_
    assert b_ == [0, 3]
    assert [[0, 1], [1, 2], [2, 5], [3, 4]] == ab

    a_, ab, b_ = match_cells(a, b, threshold=10)
    assert a_ == [3]
    assert b_ == [0, 3, 4]
    assert [[0, 1], [1, 2], [2, 5]] == ab
