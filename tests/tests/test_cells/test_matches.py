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
        "cellfinder/other_cells-z-1000-1050.xml"
    )
    cell_data = get_cells(cell_data_path)
    other_cell_data = get_cells(other_cell_data_path)
    return cell_data, other_cell_data


def as_cell(x: List[float]):
    d = np.tile(np.asarray([x]).T, (1, 3))
    cells = from_numpy_pos(d, Cell.UNKNOWN)
    return cells


@pytest.mark.xfail
def test_cell_matching_regression(cells_and_other_cells):
    cells, other_cells = cells_and_other_cells
    # TODO implement cell matching regression test here, then remove xfail
    assert False


@pytest.mark.parametrize("use_scipy", [True, False])
@pytest.mark.parametrize("pre_match", [True, False])
def test_cell_matches_equal_size(pre_match, use_scipy):
    a = as_cell([10, 20, 30, 40])
    b = as_cell([5, 15, 25, 35])
    a_, ab, b_ = match_cells(a, b, pre_match=pre_match, use_scipy=use_scipy)
    assert not a_
    assert not b_
    assert [[0, 0], [1, 1], [2, 2], [3, 3]] == ab

    a = as_cell([20, 10, 30, 40])
    b = as_cell([5, 15, 25, 35])
    a_, ab, b_ = match_cells(a, b, pre_match=pre_match, use_scipy=use_scipy)
    assert not a_
    assert not b_
    assert [[0, 1], [1, 0], [2, 2], [3, 3]] == ab

    a = as_cell([20, 10, 30, 40])
    b = as_cell([11, 22, 39, 42])
    a_, ab, b_ = match_cells(a, b, pre_match=pre_match, use_scipy=use_scipy)
    assert not a_
    assert not b_
    assert [[0, 1], [1, 0], [2, 2], [3, 3]] == ab


@pytest.mark.parametrize("use_scipy", [True, False])
@pytest.mark.parametrize("pre_match", [True, False])
def test_cell_matches_larger_other(pre_match, use_scipy):
    a = as_cell([1, 12, 100, 80])
    b = as_cell([5, 15, 25, 35, 100])
    a_, ab, b_ = match_cells(a, b, pre_match=pre_match, use_scipy=use_scipy)
    assert not a_
    assert b_ == [2]
    assert [[0, 0], [1, 1], [2, 4], [3, 3]] == ab

    a = as_cell([20, 10, 30, 40])
    b = as_cell([11, 22, 39, 42, 41])
    a_, ab, b_ = match_cells(a, b, pre_match=pre_match, use_scipy=use_scipy)
    assert not a_
    assert b_ == [3]
    assert [[0, 1], [1, 0], [2, 2], [3, 4]] == ab


@pytest.mark.parametrize("use_scipy", [True, False])
@pytest.mark.parametrize("pre_match", [True, False])
def test_cell_matches_larger_cells(pre_match, use_scipy):
    a = as_cell([5, 15, 25, 35, 100])
    b = as_cell([1, 12, 100, 80])
    a_, ab, b_ = match_cells(a, b, pre_match=pre_match, use_scipy=use_scipy)
    assert a_ == [2]
    assert not b_
    assert [[0, 0], [1, 1], [3, 3], [4, 2]] == ab


@pytest.mark.parametrize("use_scipy", [True, False])
@pytest.mark.parametrize("pre_match", [True, False])
def test_cell_matches_threshold(pre_match, use_scipy):
    a = as_cell([10, 12, 100, 80])
    b = as_cell([0, 5, 15, 25, 35, 100])
    a_, ab, b_ = match_cells(a, b, pre_match=pre_match, use_scipy=use_scipy)
    assert not a_
    assert b_ == [0, 3]
    assert [[0, 1], [1, 2], [2, 5], [3, 4]] == ab

    a_, ab, b_ = match_cells(
        a,
        b,
        threshold=math.sqrt(3) * 11,
        pre_match=pre_match,
        use_scipy=use_scipy,
    )
    assert a_ == [3]
    assert b_ == [0, 3, 4]
    assert [[0, 1], [1, 2], [2, 5]] == ab


@pytest.mark.parametrize("use_scipy", [True, False])
@pytest.mark.parametrize("pre_match", [True, False])
def test_global_optimum_with_threshold_original_pr(pre_match, use_scipy):
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
        use_scipy=use_scipy,
    )
    assert not missing_c1
    assert not missing_c2
    assert good_matches == [[0, 0], [1, 1]]

    # with threshold, the previous pairing should not be considered good.
    # Instead, only (12, 10) is a good match. So while total cost is 24,
    # we only care about the cost of 2 during the matching algorithm
    # BUT, only when not using scipy. With scipy it doesn't account for
    # threshold during the matching, so it'll do it after
    missing_c1, good_matches, missing_c2 = match_cells(
        cells1, cells2, threshold=5, pre_match=pre_match, use_scipy=use_scipy
    )
    # before we added the threshold to match_points, the following applies to
    # both scipy and our own. After the fix, this is only True for scipy
    if use_scipy:
        assert missing_c1 == [0, 1]
        assert missing_c2 == [0, 1]
        assert not good_matches
    else:
        # with threshold in match_points, this is true - as wanted
        assert missing_c1 == [
            0,
        ]
        assert missing_c2 == [
            1,
        ]
        assert good_matches == [[1, 0]]


@pytest.mark.parametrize("use_scipy", [True, False])
@pytest.mark.parametrize("pre_match", [True, False])
def test_rows_greater_than_cols(pre_match, use_scipy):
    with pytest.raises(ValueError):
        match_points(
            np.zeros((5, 3)),
            np.zeros((4, 3)),
            pre_match=pre_match,
            use_scipy=use_scipy,
        )


@pytest.mark.parametrize("use_scipy", [True, False])
@pytest.mark.parametrize("pre_match", [True, False])
def test_unequal_inputs_shape(pre_match, use_scipy):
    with pytest.raises(ValueError):
        match_points(
            np.zeros((5, 3)),
            np.zeros((5, 2)),
            pre_match=pre_match,
            use_scipy=use_scipy,
        )


@pytest.mark.parametrize("use_scipy", [True, False])
@pytest.mark.parametrize("pre_match", [True, False])
def test_bad_input_shape(pre_match, use_scipy):
    # has to be 2 dims
    with pytest.raises(ValueError):
        match_points(
            np.zeros(5), np.zeros(5), pre_match=pre_match, use_scipy=use_scipy
        )

    with pytest.raises(ValueError):
        match_points(
            np.zeros((5, 4, 6)),
            np.zeros((5, 4, 6)),
            pre_match=pre_match,
            use_scipy=use_scipy,
        )


@pytest.mark.parametrize("use_scipy", [True, False])
@pytest.mark.parametrize("pre_match", [True, False])
def test_progress_already_running(pre_match, use_scipy):
    a = as_cell([10, 12])
    b = as_cell([10, 12])
    cell_utils.__progress_update.updater = 1

    try:
        with pytest.raises(TypeError):
            match_cells(a, b, pre_match=pre_match, use_scipy=use_scipy)
    finally:
        cell_utils.__progress_update.updater = None


@pytest.mark.parametrize("use_scipy", [True, False])
@pytest.mark.parametrize("pre_match", [True, False])
def test_distance_too_large(pre_match, use_scipy):
    a = np.array([[1, 2, 3]]).T
    b = np.array([[1, 2, np.inf]]).T
    with pytest.raises(ValueError):
        match_points(a, b, pre_match=pre_match, use_scipy=use_scipy)


@pytest.mark.parametrize("use_scipy", [True, False])
@pytest.mark.parametrize("pre_match", [True, False])
def test_contains_identical_points(pre_match, use_scipy):
    a = np.array([[1, 10], [5, 7], [22, 12]])
    b = np.array([[5, 7], [7, 1], [21, 10]])
    matching = match_points(a, b, pre_match=pre_match, use_scipy=use_scipy)
    assert np.array_equal(matching, [1, 0, 2])


@pytest.mark.parametrize("use_scipy", [True, False])
@pytest.mark.parametrize("pre_match", [True, False])
def test_contains_only_identical_points(pre_match, use_scipy):
    a = np.array([[1, 2, 3]]).T
    b = np.array([[2, 3, 5, 1]]).T
    matching = match_points(a, b, pre_match=pre_match, use_scipy=use_scipy)
    assert np.array_equal(matching, [3, 0, 1])


@pytest.mark.parametrize("use_scipy", [True, False])
@pytest.mark.parametrize("pre_match", [True, False])
def test_contains_no_identical_points(pre_match, use_scipy):
    a = np.array([[1, 10], [5, 7], [22, 12]])
    b = np.array([[6, 7], [7, 1], [21, 10]])
    matching = match_points(a, b, pre_match=pre_match, use_scipy=use_scipy)
    assert np.array_equal(matching, [1, 0, 2])
