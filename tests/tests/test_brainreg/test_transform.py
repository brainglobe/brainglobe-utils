from pathlib import Path

import numpy as np
import pytest
from brainglobe_atlasapi import BrainGlobeAtlas

from brainglobe_utils.brainreg.transform import (
    transform_points_from_downsampled_to_atlas_space,
)


@pytest.mark.parametrize(
    (
        "mock_deformation_field",
        "expected_transformed_points",
        "expected_points_out_of_bounds",
    ),
    [
        (np.ones((132, 80, 114)), [[10, 10, 10], [10, 10, 10]], []),
        (np.ones((4, 4, 4)), np.atleast_3d([]), [[5, 5, 5], [6, 6, 6]]),
    ],
)
def test_transform_points_from_downsampled_to_atlas_space(
    mocker,
    mock_deformation_field,
    expected_transformed_points,
    expected_points_out_of_bounds,
):
    """
    Test case for transforming points from downsampled space to atlas space.
    * check that deformation field of ones maps to 1,1,1*resolution
    * check that too small deformation field maps points to out-of-bounds

    Parameters
    ----------
    mocker : pytest_mock.plugin.MockerFixture
        The mocker object used to patch the reading of deformation
        field tiffs.
    """
    mocker.patch(
        "brainglobe_utils.brainreg.transform.tifffile.imread",
        side_effect=lambda x: mock_deformation_field,
    )
    downsampled_points = np.array([[5, 5, 5], [6, 6, 6]])
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
    assert np.all(transformed_points == expected_transformed_points)
    assert points_out_of_bounds == expected_points_out_of_bounds
