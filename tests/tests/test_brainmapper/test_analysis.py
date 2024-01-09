import filecmp
from pathlib import Path

import pytest

from brainglobe_utils.brainmapper.analysis import (
    Point,
    count_points_per_brain_region,
)


@pytest.fixture
def points():
    p1 = Point(
        raw_coordinate=[1.0, 1.0, 1.0],
        atlas_coordinate=[1.0, 1.0, 1.0],
        structure="Paraventricular hypothalamic nucleus, descending division",
        structure_id=56,
        hemisphere="right",
    )
    p2 = Point(
        raw_coordinate=[2.0, 2.0, 2.0],
        atlas_coordinate=[2.0, 2.0, 2.0],
        structure="Anterodorsal nucleus",
        structure_id=57,
        hemisphere="left",
    )
    return [p1, p2]


@pytest.fixture
def structures_with_points():
    return [
        "Paraventricular hypothalamic nucleus, descending division",
        "Anterodorsal nucleus",
    ]


def test_get_region_totals(tmp_path, points, structures_with_points):
    """Regression test for count_points_per_brain_region for
    pandas 1.5.3 -> 2.1.3+.
    pd.Dataframe.append was deprecated and removed in this time."""
    OUTPUT_DATA_LOC = (
        Path(__file__).parent.parent.parent / "data" / "brainmapper"
    )

    volumes_path = OUTPUT_DATA_LOC / "volumes.csv"
    expected_output = (
        OUTPUT_DATA_LOC / "region_totals_regression_pandas1_5_3.csv"
    )

    output_path = Path(tmp_path / "tmp_region_totals.csv")
    count_points_per_brain_region(
        points, structures_with_points, volumes_path, output_path
    )
    assert output_path.exists()
    assert filecmp.cmp(output_path, expected_output)
