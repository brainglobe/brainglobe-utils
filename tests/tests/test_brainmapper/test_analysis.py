from pathlib import Path

import pandas as pd
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
    """
    Regression test for count_points_per_brain_region for
    pandas 1.5.3 -> 2.1.3+.
    pd.DataFrame.append was deprecated and removed in this time.

    2024-01-31: Newer versions of pandas are writing the
    DataFrame rows in a different order. As such, filecmp is no longer
    sufficient to check that we are still counting the number of cells
    correctly - we will need to load the data back in and do a pandas
    comparison.
    """
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

    # Read data back in, and sort rows by the structures for comparison.
    # NOTE: Column 'structure name' should exist, otherwise we've failed
    # and the test will flag the error appropriately
    expected_df = (
        pd.read_csv(expected_output)
        .sort_values("structure_name")
        .reset_index(drop=True)
    )
    produced_df = (
        pd.read_csv(output_path)
        .sort_values("structure_name")
        .reset_index(drop=True)
    )
    assert expected_df.equals(
        produced_df
    ), "Produced DataFrame no longer matches per-region "
    "count from expected DataFrame"
