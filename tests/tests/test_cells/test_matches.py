import math
from typing import List

import numpy as np
import pytest

import brainglobe_utils.cells.cells as cell_utils
from brainglobe_utils.cells.cells import (
    Cell,
    from_numpy_pos,
    match_cells,
    match_points,
)


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

    a_, ab, b_ = match_cells(a, b, threshold=math.sqrt(3) * 11)
    assert a_ == [3]
    assert b_ == [0, 3, 4]
    assert [[0, 1], [1, 2], [2, 5]] == ab


def test_global_optimum_with_threshold_original_pr():
    cells1 = [
        Cell((0, 0, 0), Cell.UNKNOWN),
        Cell((12, 0, 0), Cell.UNKNOWN),
    ]
    cells2 = [
        Cell((10, 0, 0), Cell.UNKNOWN),
        Cell((22, 0, 0), Cell.UNKNOWN),
    ]

    # without threshold, the global optimum pars points (0, 10), (12, 22) at a
    # global cost of 20. The other pairing would have cost of 24
    missing_c1, good_matches, missing_c2 = match_cells(
        cells1, cells2, threshold=np.inf
    )
    assert not missing_c1
    assert not missing_c2
    assert good_matches == [[0, 0], [1, 1]]

    # with threshold, the previous pairing should not be considered good.
    # Instead, only (12, 10) is a good match. So while total cost is 24,
    # we only care about the cost of 2 during the matching algorithm
    missing_c1, good_matches, missing_c2 = match_cells(
        cells1, cells2, threshold=5
    )
    # before we added the threshold to match_points, the following applies
    # assert missing_c1 == [0, 1]
    # assert missing_c2 == [0, 1]
    # assert not good_matches
    # with threshold in match_points, this is true - as wanted
    assert missing_c1 == [
        0,
    ]
    assert missing_c2 == [
        1,
    ]
    assert good_matches == [[1, 0]]


def test_rows_greater_than_cols():
    with pytest.raises(ValueError):
        match_points(np.zeros((5, 3)), np.zeros((4, 3)))


def test_unequal_inputs_shape():
    with pytest.raises(ValueError):
        match_points(np.zeros((5, 3)), np.zeros((5, 2)))


def test_bad_input_shape():
    # we want to check that a 1-dim array is not accepted. But, numba checks
    # the inputs for at least 2-dims because it knows we access the 2dn dim.
    # So we have no chance to raise an error ourself. So check numba's error
    import numba.core.errors

    with pytest.raises(numba.core.errors.TypingError):
        match_points(np.zeros(5), np.zeros(5))

    with pytest.raises(ValueError):
        match_points(np.zeros((5, 4, 6)), np.zeros((5, 4, 6)))


def test_progress_already_running():
    a = as_cell([10, 12])
    b = as_cell([10, 12])
    cell_utils.__progress_update.updater = 1

    try:
        with pytest.raises(TypeError):
            match_cells(a, b)
    finally:
        cell_utils.__progress_update.updater = None


def test_distance_too_large():
    a = np.array([[1, 2, 3]])
    b = np.array([[1, 2, np.inf]])
    with pytest.raises(ValueError):
        match_points(a, b)
