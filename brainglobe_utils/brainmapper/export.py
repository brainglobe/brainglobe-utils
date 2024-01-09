from pathlib import Path
from typing import Union

import numpy as np


def export_points_to_brainrender(
    points: np.ndarray,
    resolution: float,
    output_filename: Union[str, Path],
) -> None:
    """
    Export points in atlas space for visualization in brainrender.

    Points are scaled from atlas coordinates to real units and saved
    as a numpy file.

    Parameters
    ----------
    points : np.ndarray
        A numpy array containing the points in atlas space.
    resolution : float
        A numerical value representing the resolution scale to be
        applied to the points.
    output_filename : Union[str, Path]
        The path where the numpy file will be saved. Can be a string
        or a Path object.

    Returns
    -------
    None
    """
    np.save(output_filename, points * resolution)
