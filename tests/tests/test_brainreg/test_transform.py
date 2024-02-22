from pathlib import Path

import numpy as np
from bg_atlasapi import BrainGlobeAtlas

from brainglobe_utils.brainreg.transform import (
    transform_points_from_downsampled_to_atlas_space,
)


def test_transform_points_from_downsampled_to_atlas_space(mocker):
    """
    Test case for transforming points from downsampled space to atlas space.
    This is a basic test case that covers a deformation field that maps everything to [1, 1, 1].

    Args:
        mocker: The mocker object used to patch the reading of deformation field tiffs.

    Returns:
        None
    """
    mock_deformation_field = np.ones(
        (132, 80, 114)
    )  # shape of allen 100 reference, has unit mm
    mocker.patch(
        "brainglobe_utils.brainreg.transform.tifffile.imread",
        side_effect=lambda x: mock_deformation_field,
    )
    downsampled_points = np.array([[1, 1, 1], [2, 2, 2]])
    transformed_points, points_out_of_bounds = (
        transform_points_from_downsampled_to_atlas_space(
            downsampled_points=downsampled_points,
            atlas=BrainGlobeAtlas("allen_mouse_100um"),
            deformation_field_paths=[
                Path.home() / "dummy_x_deformation.tif",
                Path.home() / "dummy_y_deformation.tif",
                Path.home() / "dummy_z_deformation.tif",
            ],
        )
    )
    # because we mock the deformation field as all ones,
    # all coordinates should be mapped to [1,1,1]*1mm/100um = [10,10,10]
    assert np.all(transformed_points == np.ones_like(transformed_points) * 10)
    assert not points_out_of_bounds, str(points_out_of_bounds)


def test_transform_points_from_downsampled_to_atlas_space_out_of_bounds(
    mocker,
):
    """
    Test case for transforming points from downsampled space to atlas space when points are out of bounds.
    Points are out of bounds when they cause an index error on the deformation field.

    Args:
        mocker: The mocker object to patch the reading of deformation field tiffs

    Returns:
        None
    """
    mock_deformation_field = np.ones((4, 4, 4))
    mocker.patch(
        "brainglobe_utils.brainreg.transform.tifffile.imread",
        side_effect=lambda x: mock_deformation_field,
    )
    downsampled_points = np.array([[5, 5, 5]])
    transformed_points, points_out_of_bounds = (
        transform_points_from_downsampled_to_atlas_space(
            downsampled_points=downsampled_points,
            atlas=BrainGlobeAtlas("allen_mouse_100um"),
            deformation_field_paths=[
                Path.home() / "dummy_x_deformation.tif",
                Path.home() / "dummy_y_deformation.tif",
                Path.home() / "dummy_z_deformation.tif",
            ],
        )
    )

    assert len(transformed_points) == 0
    assert len(points_out_of_bounds) == 1
    assert points_out_of_bounds[0] == [5, 5, 5]
