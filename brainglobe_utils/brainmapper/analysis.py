"""
Parts based on https://github.com/SainsburyWellcomeCentre/cell_count_analysis
by Charly Rousseau (https://github.com/crousseau).
"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Set, Union

import numpy as np
import pandas as pd
from brainglobe_atlasapi import BrainGlobeAtlas

from brainglobe_utils.general.system import ensure_directory_exists
from brainglobe_utils.pandas.misc import safe_pandas_concat, sanitise_df


@dataclass
class Point:
    """
    A class to represent a point in both raw and atlas coordinate spaces,
    along with associated anatomical information.

    Attributes
    ----------
    raw_coordinate : np.ndarray
        A numpy array representing the raw coordinates of the point
        in the original image space.
    atlas_coordinate : np.ndarray
        A numpy array representing the coordinates of the point in atlas space.
    structure : str
        The name of the atlas structure associated with the point.
    structure_id : int
        The numerical ID of the anatomical structure associated with the point.
    hemisphere : str
        The hemisphere ('left' or 'right') in which the point is located.

    """

    raw_coordinate: np.ndarray
    atlas_coordinate: np.ndarray
    structure: str
    structure_id: int
    hemisphere: str


def calculate_densities(
    counts: pd.DataFrame, volume_csv_path: Union[str, Path]
) -> pd.DataFrame:
    """
    Use region volumes from registration to calculate cell densities.

    Parameters
    ----------
    counts : pd.DataFrame
        Dataframe with cell counts.
    volume_csv_path : Union[str, Path]
        Path of the CSV file containing the volumes of each brain region.

    Returns
    -------
    pd.DataFrame
        A dataframe containing the original cell counts and the calculated cell
        densities per mm³ for each brain region.

    """

    volumes = pd.read_csv(volume_csv_path, sep=",", header=0, quotechar='"')
    df = pd.merge(counts, volumes, on="structure_name", how="outer")
    df = df.fillna(0)
    df["left_cells_per_mm3"] = df.left_cell_count / df.left_volume_mm3
    df["right_cells_per_mm3"] = df.right_cell_count / df.right_volume_mm3
    return df


def combine_df_hemispheres(df: pd.DataFrame) -> pd.DataFrame:
    """
    Combine left and right hemisphere data onto a single row

    Parameters
    ----------
    df : pd.DataFrame
        A pandas DataFrame with separate rows for left and
        right hemisphere data.

    Returns
    -------
    pd.DataFrame
        A DataFrame with combined hemisphere data. Each row
        represents the combined data of left and right hemispheres for
        each brain region.

    """
    left = df[df["hemisphere"] == "left"]
    right = df[df["hemisphere"] == "right"]
    left = left.drop(["hemisphere"], axis=1)
    right = right.drop(["hemisphere"], axis=1)
    left.rename(columns={"cell_count": "left_cell_count"}, inplace=True)
    right.rename(columns={"cell_count": "right_cell_count"}, inplace=True)
    both = pd.merge(left, right, on="structure_name", how="outer")
    both = both.fillna(0)
    both["total_cells"] = both.left_cell_count + both.right_cell_count
    both = both.sort_values("total_cells", ascending=False)
    return both


def create_all_cell_df(points: List[Point]) -> None:
    """
    This function takes a list of Point objects, each representing cell
    coordinates and brain region and converts this into a pandas DataFrame.

    Parameters
    ----------
    points : List[Point]
        A list of Point objects, each containing cell data such as
        raw and atlas coordinates,
        structure name, and hemisphere information.

    Returns
    -------
    df: pd.DataFrame
    """

    df = pd.DataFrame(
        columns=(
            "coordinate_raw_axis_0",
            "coordinate_raw_axis_1",
            "coordinate_raw_axis_2",
            "coordinate_atlas_axis_0",
            "coordinate_atlas_axis_1",
            "coordinate_atlas_axis_2",
            "structure_name",
            "hemisphere",
        )
    )

    temp_matrix = [[] for i in range(len(points))]
    for i, point in enumerate(points):
        temp_matrix[i].append(point.raw_coordinate[0])
        temp_matrix[i].append(point.raw_coordinate[1])
        temp_matrix[i].append(point.raw_coordinate[2])
        temp_matrix[i].append(point.atlas_coordinate[0])
        temp_matrix[i].append(point.atlas_coordinate[1])
        temp_matrix[i].append(point.atlas_coordinate[2])
        temp_matrix[i].append(point.structure)
        temp_matrix[i].append(point.hemisphere)

    df = pd.DataFrame(temp_matrix, columns=df.columns, index=None)
    return df


def count_points_per_brain_region(
    points: List[Point],
    structures_with_points: Set[str],
    brainreg_volume_csv_path: Union[str, Path],
) -> None:
    """
    Count the number of points per brain region.

    Parameters
    ----------
    points : List[Point]
        A list of Point objects.
    structures_with_points : Set[str]
        A set of strings representing the names of all atlas structures
        represented
    brainreg_volume_csv_path : Union[str, Path]
        The path to the CSV file containing volume information from the
        brainreg registration.


    Returns
    -------
    df: pd.DataFrame
    """

    structures_with_points = list(structures_with_points)

    point_numbers = pd.DataFrame(
        columns=("structure_name", "hemisphere", "cell_count")
    )
    for structure in structures_with_points:
        for hemisphere in ("left", "right"):
            n_points = len(
                [
                    point
                    for point in points
                    if point.structure == structure
                    and point.hemisphere == hemisphere
                ]
            )
            if n_points:
                point_numbers = safe_pandas_concat(
                    point_numbers,
                    pd.DataFrame(
                        data=[[structure, hemisphere, n_points]],
                        columns=[
                            "structure_name",
                            "hemisphere",
                            "cell_count",
                        ],
                    ),
                )
    sorted_point_numbers = point_numbers.sort_values(
        by=["cell_count"], ascending=False
    )

    combined_hemispheres = combine_df_hemispheres(sorted_point_numbers)
    df = calculate_densities(combined_hemispheres, brainreg_volume_csv_path)
    df = sanitise_df(df)
    return df


def summarise_points_by_atlas_region(
    points_in_raw_data_space: np.ndarray,
    points_in_atlas_space: np.ndarray,
    atlas: BrainGlobeAtlas,
    brainreg_volume_csv_path: Optional[os.PathLike] = None,
    points_list_output_filename: Optional[os.PathLike] = None,
    summary_filename: Optional[os.PathLike] = None,
) -> None:
    """
    Summarise points data by atlas region.

    This function takes points in both raw data space and atlas space,
    and generates a summary of these points based on the BrainGlobe atlas
    region they are found in.
    The summary is saved to a CSV file.

    Parameters
    ----------
    points_in_raw_data_space : np.ndarray
        A numpy array representing points in the raw data space.
        The shape of the array should be (n_points, 3).
    points_in_atlas_space : np.ndarray
        A numpy array representing points in the atlas space.
        The shape of the array should be (n_points, 3).
    atlas : BrainGlobeAtlas
        The BrainGlobe atlas object used for the analysis
    brainreg_volume_csv_path : Union[str, Path]
        The path to the CSV file containing volume information from the
        brainreg registration.
    points_list_output_filename : Union[str, Path]
        The csv path where the detailed points list will be saved.
    summary_filename : Union[str, Path]
        The csv path where the summary of points by atlas region will be saved.

    Returns
    -------
    None
    """

    points = []
    structures_with_points = set()
    for idx, point in enumerate(points_in_atlas_space):
        try:
            structure_id = atlas.structure_from_coords(point)
            structure = atlas.structures[structure_id]["name"]
            hemisphere = atlas.hemisphere_from_coords(point, as_string=True)
            points.append(
                Point(
                    points_in_raw_data_space[idx],
                    point,
                    structure,
                    structure_id,
                    hemisphere,
                )
            )
            structures_with_points.add(structure)
        except Exception:
            continue

    all_cell_df = create_all_cell_df(points)

    if points_list_output_filename is not None:
        ensure_directory_exists(Path(points_list_output_filename).parent)
        all_cell_df.to_csv(points_list_output_filename, index=False)

    points_per_region_df = count_points_per_brain_region(
        points,
        structures_with_points,
        brainreg_volume_csv_path,
    )

    if summary_filename is not None:
        points_per_region_df.to_csv(summary_filename, index=False)

    return all_cell_df, points_per_region_df
