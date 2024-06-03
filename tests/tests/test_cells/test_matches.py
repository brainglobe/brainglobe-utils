import math
from typing import List

import numpy as np
import pytest
from scipy.optimize import linear_sum_assignment

import brainglobe_utils.cells.cells as cell_utils
from brainglobe_utils.cells.cells import (
    Cell,
    analyze_point_matches,
    from_numpy_pos,
    match_cells,
    match_points,
    to_numpy_pos,
)
from brainglobe_utils.IO.cells import get_cells


@pytest.fixture
def cells_and_other_cells(test_data_registry):
    """
    Provides real-life cell coordinates from a CFOS-labelled brain from
    two different cellfinder versions (pre- and post cellfinder PR #398).
    Intended to be used for regression testing our cell matching code.

    Parameters
    ----------
    test_data_registry : Pooch.pooch
        The BrainGlobe test data registry.

    Returns
    -------
    cell_data : List[Cell]
        The loaded cell data.

    """
    cell_data_path = test_data_registry.fetch(
        "cellfinder/cells-z-1000-1050.xml"
    )
    other_cell_data_path = test_data_registry.fetch(
        "cellfinder/other-cells-z-1000-1050.xml"
    )
    cell_data = get_cells(cell_data_path)
    other_cell_data = get_cells(other_cell_data_path)
    return cell_data, other_cell_data


def as_cell(x: List[float]):
    d = np.tile(np.asarray([x]).T, (1, 3))
    cells = from_numpy_pos(d, Cell.UNKNOWN)
    return cells


def test_cell_matching_regression(cells_and_other_cells):
    cells, other_cells = cells_and_other_cells
    np_cells = to_numpy_pos(cells)
    np_other = to_numpy_pos(other_cells)

    # only run matching on unpaired to reduce computation
    unpaired1_indices, unpaired2_indices, paired_indices = (
        cell_utils._find_identical_points(np_cells, np_other)
    )
    np_cells = np_cells[unpaired1_indices]
    np_other = np_other[unpaired2_indices]

    # happens to be true for this dataset
    assert len(np_cells) < len(np_other), "must be true to pass to match"

    # get matches
    matches = match_points(np_cells, np_other, pre_match=False)
    missing_cells, good, missing_other = analyze_point_matches(
        np_cells, np_other, matches
    )
    good = np.array(good)
    assert not len(missing_cells), "all cells must be matched"

    # get cost
    a = np_cells[good[:, 0], :]
    b = np_other[good[:, 1], :]
    cost_our = np.sum(np.sqrt(np.sum(np.square(a - b), axis=1)))

    # get scipy cost
    # Mxk -> M1K
    pos1 = np_cells[:, np.newaxis, :]
    # Nxk -> 1NK
    pos2 = np_other[np.newaxis, :, :]
    # dist is MNK
    dist = pos1 - pos2
    # cost is MN
    cost_mat = np.sqrt(np.sum(np.square(dist), axis=2))
    # result is sorted by rows
    rows, cols = linear_sum_assignment(cost_mat)

    cost_scipy = cost_mat[rows, cols].sum()

    assert np.isclose(cost_scipy, cost_our)


@pytest.mark.parametrize("pre_match", [True, False])
def test_cell_matches_equal_size(pre_match):
    a = as_cell([10, 20, 30, 40])
    b = as_cell([5, 15, 25, 35])
    a_, ab, b_ = match_cells(a, b, pre_match=pre_match)
    assert not a_
    assert not b_
    assert [[0, 0], [1, 1], [2, 2], [3, 3]] == ab

    a = as_cell([20, 10, 30, 40])
    b = as_cell([5, 15, 25, 35])
    a_, ab, b_ = match_cells(a, b, pre_match=pre_match)
    assert not a_
    assert not b_
    assert [[0, 1], [1, 0], [2, 2], [3, 3]] == ab

    a = as_cell([20, 10, 30, 40])
    b = as_cell([11, 22, 39, 42])
    a_, ab, b_ = match_cells(a, b, pre_match=pre_match)
    assert not a_
    assert not b_
    assert [[0, 1], [1, 0], [2, 2], [3, 3]] == ab


@pytest.mark.parametrize("pre_match", [True, False])
def test_cell_matches_larger_other(pre_match):
    a = as_cell([1, 12, 100, 80])
    b = as_cell([5, 15, 25, 35, 100])
    a_, ab, b_ = match_cells(a, b, pre_match=pre_match)
    assert not a_
    assert b_ == [2]
    assert [[0, 0], [1, 1], [2, 4], [3, 3]] == ab

    a = as_cell([20, 10, 30, 40])
    b = as_cell([11, 22, 39, 42, 41])
    a_, ab, b_ = match_cells(a, b, pre_match=pre_match)
    assert not a_
    assert b_ == [3]
    assert [[0, 1], [1, 0], [2, 2], [3, 4]] == ab


@pytest.mark.parametrize("pre_match", [True, False])
def test_cell_matches_larger_cells(pre_match):
    a = as_cell([5, 15, 25, 35, 100])
    b = as_cell([1, 12, 100, 80])
    a_, ab, b_ = match_cells(a, b, pre_match=pre_match)
    assert a_ == [2]
    assert not b_
    assert [[0, 0], [1, 1], [3, 3], [4, 2]] == ab


@pytest.mark.parametrize("pre_match", [True, False])
def test_cell_matches_threshold(pre_match):
    a = as_cell([10, 12, 100, 80])
    b = as_cell([0, 5, 15, 25, 35, 100])
    a_, ab, b_ = match_cells(a, b, pre_match=pre_match)
    assert not a_
    assert b_ == [0, 3]
    assert [[0, 1], [1, 2], [2, 5], [3, 4]] == ab

    a_, ab, b_ = match_cells(
        a,
        b,
        threshold=math.sqrt(3) * 11,
        pre_match=pre_match,
    )
    assert a_ == [3]
    assert b_ == [0, 3, 4]
    assert [[0, 1], [1, 2], [2, 5]] == ab


@pytest.mark.parametrize("pre_match", [True, False])
def test_global_optimum_with_threshold_original_pr(pre_match):
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
        cells1,
        cells2,
        threshold=np.inf,
        pre_match=pre_match,
    )
    assert not missing_c1
    assert not missing_c2
    assert good_matches == [[0, 0], [1, 1]]

    # with threshold, the previous pairing should not be considered good.
    # Instead, only (12, 10) is a good match. So while total cost is 24,
    # we only care about the cost of 2 during the matching algorithm
    missing_c1, good_matches, missing_c2 = match_cells(
        cells1, cells2, threshold=5, pre_match=pre_match
    )
    assert missing_c1 == [
        0,
    ]
    assert missing_c2 == [
        1,
    ]
    assert good_matches == [[1, 0]]


@pytest.mark.parametrize("pre_match", [True, False])
def test_rows_greater_than_cols(pre_match):
    with pytest.raises(ValueError):
        match_points(
            np.zeros((5, 3)),
            np.zeros((4, 3)),
            pre_match=pre_match,
        )


@pytest.mark.parametrize("pre_match", [True, False])
def test_unequal_inputs_shape(pre_match):
    with pytest.raises(ValueError):
        match_points(
            np.zeros((5, 3)),
            np.zeros((5, 2)),
            pre_match=pre_match,
        )


@pytest.mark.parametrize("pre_match", [True, False])
def test_bad_input_shape(pre_match):
    # has to be 2 dims
    with pytest.raises(ValueError):
        match_points(np.zeros(5), np.zeros(5), pre_match=pre_match)

    with pytest.raises(ValueError):
        match_points(
            np.zeros((5, 4, 6)),
            np.zeros((5, 4, 6)),
            pre_match=pre_match,
        )


@pytest.mark.parametrize("pre_match", [True, False])
def test_progress_already_running(pre_match):
    a = as_cell([10, 12])
    b = as_cell([10, 12])
    cell_utils.__progress_update.updater = 1

    try:
        with pytest.raises(TypeError):
            match_cells(a, b, pre_match=pre_match)
    finally:
        cell_utils.__progress_update.updater = None


@pytest.mark.parametrize("pre_match", [True, False])
def test_distance_too_large(pre_match):
    a = np.array([[1, 2, 3]]).T
    b = np.array([[1, 2, np.inf]]).T
    with pytest.raises(ValueError):
        match_points(a, b, pre_match=pre_match)


@pytest.mark.parametrize("pre_match", [True, False])
def test_contains_identical_points(pre_match):
    a = np.array([[1, 10], [5, 7], [22, 12]])
    b = np.array([[5, 7], [7, 1], [21, 10]])
    matching = match_points(a, b, pre_match=pre_match)
    assert np.array_equal(matching, [1, 0, 2])


@pytest.mark.parametrize("pre_match", [True, False])
def test_contains_only_identical_points(pre_match):
    a = np.array([[1, 2, 3]]).T
    b = np.array([[2, 3, 5, 1]]).T
    matching = match_points(a, b, pre_match=pre_match)
    assert np.array_equal(matching, [3, 0, 1])


@pytest.mark.parametrize("pre_match", [True, False])
def test_contains_no_identical_points(pre_match):
    a = np.array([[1, 10], [5, 7], [22, 12]])
    b = np.array([[6, 7], [7, 1], [21, 10]])
    matching = match_points(a, b, pre_match=pre_match)
    assert np.array_equal(matching, [1, 0, 2])
