from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from brainglobe_atlasapi import BrainGlobeAtlas

from brainglobe_utils.brainmapper.analysis import (
    Point,
    count_points_per_brain_region,
    summarise_points_by_atlas_region,
)


@pytest.fixture
def points():
    p1 = Point(
        raw_coordinate=np.array([1.0, 1.0, 1.0]),
        atlas_coordinate=np.array([1.0, 1.0, 1.0]),
        structure="Paraventricular hypothalamic nucleus, descending division",
        structure_id=56,
        hemisphere="right",
    )
    p2 = Point(
        raw_coordinate=np.array([2.0, 2.0, 2.0]),
        atlas_coordinate=np.array([2.0, 2.0, 2.0]),
        structure="Anterodorsal nucleus",
        structure_id=57,
        hemisphere="left",
    )
    return [p1, p2]


@pytest.fixture
def points_mouse():
    """
    List of points in different regions of the allen mouse brain atlas 100um.
    All values are correct except for the raw_coordinate, which is set to an
    arbitrary value.
    """
    return [
        Point(
            raw_coordinate=np.array([1.0, 1.0, 1.0]),
            atlas_coordinate=np.array([61.0, 33.77, 48.99]),
            structure="Anterodorsal nucleus",
            structure_id=64,
            hemisphere="right",
        ),
        Point(
            raw_coordinate=np.array([2.0, 2.0, 2.0]),
            atlas_coordinate=np.array([61.0, 33.55, 64.71]),
            structure="Anterodorsal nucleus",
            structure_id=64,
            hemisphere="left",
        ),
        Point(
            raw_coordinate=np.array([3.0, 3.0, 3.0]),
            atlas_coordinate=np.array([63.0, 33.07, 65.15]),
            structure="Anterodorsal nucleus",
            structure_id=64,
            hemisphere="left",
        ),
        Point(
            raw_coordinate=np.array([4.0, 4.0, 4.0]),
            atlas_coordinate=np.array([65.0, 56.42, 53.38]),
            structure="Paraventricular hypothalamic nucleus, descending "
            "division",
            structure_id=63,
            hemisphere="right",
        ),
        Point(
            raw_coordinate=np.array([5.0, 5.0, 5.0]),
            atlas_coordinate=np.array([65.0, 56.55, 60.16]),
            structure="Paraventricular hypothalamic nucleus, descending "
            "division",
            structure_id=63,
            hemisphere="left",
        ),
        Point(
            raw_coordinate=np.array([6.0, 6.0, 6.0]),
            atlas_coordinate=np.array([66.0, 56.60, 60.29]),
            structure="Paraventricular hypothalamic nucleus, descending "
            "division",
            structure_id=63,
            hemisphere="left",
        ),
    ]


@pytest.fixture
def structures_with_points():
    return [
        "Paraventricular hypothalamic nucleus, descending division",
        "Anterodorsal nucleus",
    ]


@pytest.fixture
def points_in_raw_data_space(points_mouse):
    """Numpy array of raw point coordinates"""
    raw_points = []
    for point in points_mouse:
        raw_points.append(
            [
                point.raw_coordinate[0],
                point.raw_coordinate[1],
                point.raw_coordinate[2],
            ]
        )
    return np.array(raw_points)


@pytest.fixture
def points_in_atlas_space(points_mouse):
    """Numpy array of atlas point coordinates"""
    atlas_points = []
    for point in points_mouse:
        atlas_points.append(
            [
                point.atlas_coordinate[0],
                point.atlas_coordinate[1],
                point.atlas_coordinate[2],
            ]
        )
    return np.array(atlas_points)


@pytest.fixture
def atlas(tmp_path):
    """Get the allen mouse 100um atlas"""
    return BrainGlobeAtlas("allen_mouse_100um")


@pytest.fixture
def brainmapper_data_path():
    """Directory storing all brainmapper test data"""
    return Path(__file__).parent.parent.parent / "data" / "brainmapper"


@pytest.fixture
def volumes_path(brainmapper_data_path):
    """
    Path of csv file summarising volumes of a small subset of the regions
    in the mouse brain
    """
    return brainmapper_data_path / "volumes.csv"


def test_get_region_totals(
    tmp_path,
    points,
    structures_with_points,
    brainmapper_data_path,
    volumes_path,
):
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
    expected_output = (
        brainmapper_data_path / "region_totals_regression_pandas1_5_3.csv"
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


def test_summarise_points_by_region(
    tmp_path,
    atlas,
    points_mouse,
    points_in_raw_data_space,
    points_in_atlas_space,
    volumes_path,
):
    """
    Test that summarise_points_by_atlas_region correctly produces both a
    points_list csv (summarising coordinates / regions of all points) and
    a summary csv (containing cell counts / volume summaries per region)
    """

    points_list_path = tmp_path / "points_list.csv"
    summary_path = tmp_path / "summary.csv"

    summarise_points_by_atlas_region(
        points_in_raw_data_space,
        points_in_atlas_space,
        atlas,
        volumes_path,
        points_list_path,
        summary_path,
    )

    # read all results, and original volume csv file
    points_list_df = pd.read_csv(points_list_path)
    summary_df = pd.read_csv(summary_path)
    volumes_df = pd.read_csv(volumes_path)

    counts_by_region = {}

    # Test that each point is correctly written into the points list csv file
    for index, row in points_list_df.iterrows():
        assert row.structure_name == points_mouse[index].structure
        assert row.hemisphere == points_mouse[index].hemisphere
        raw_coord = row.loc[
            "coordinate_raw_axis_0":"coordinate_raw_axis_2"
        ].to_numpy()
        atlas_coord = row.loc[
            "coordinate_atlas_axis_0":"coordinate_atlas_axis_2"
        ].to_numpy()
        assert (raw_coord == points_mouse[index].raw_coordinate).all()
        assert (atlas_coord == points_mouse[index].atlas_coordinate).all()

        # Keep track of cell counts per brain region
        if row.structure_name not in counts_by_region:
            counts_by_region[row.structure_name] = [0, 0]
        if row.hemisphere == "left":
            counts_by_region[row.structure_name][0] += 1
        else:
            counts_by_region[row.structure_name][1] += 1

    assert (summary_df.left_cell_count + summary_df.right_cell_count).equals(
        summary_df.total_cells
    )
    assert (summary_df.left_volume_mm3 + summary_df.right_volume_mm3).equals(
        summary_df.total_volume_mm3
    )
    assert (summary_df.left_cell_count / summary_df.left_volume_mm3).equals(
        summary_df.left_cells_per_mm3
    )
    assert (summary_df.right_cell_count / summary_df.right_volume_mm3).equals(
        summary_df.right_cells_per_mm3
    )

    # Check volumes in summary df match the original volumes csv file
    joined = pd.merge(summary_df, volumes_df, on="structure_name", how="outer")
    joined = joined.fillna(0)
    assert joined.left_volume_mm3_x.equals(joined.left_volume_mm3_y)
    assert joined.right_volume_mm3_x.equals(joined.right_volume_mm3_y)
    assert joined.total_volume_mm3_x.equals(joined.total_volume_mm3_y)

    # Check cell counts per region/hemisphere in summary_df match input points
    cell_counts = pd.DataFrame.from_dict(
        counts_by_region,
        orient="index",
        columns=("left_cell_count", "right_cell_count"),
    )
    cell_counts.index.name = "structure_name"
    cell_counts.reset_index(inplace=True)
    joined = pd.merge(
        summary_df, cell_counts, on="structure_name", how="outer"
    )
    joined = joined.fillna(0)
    assert joined.left_cell_count_x.equals(joined.left_cell_count_y)
    assert joined.right_cell_count_x.equals(joined.right_cell_count_y)
