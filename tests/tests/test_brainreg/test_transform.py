from pathlib import Path

import brainglobe_space as bgs
import numpy as np
import pytest
from brainglobe_atlasapi import BrainGlobeAtlas

from brainglobe_utils.brainreg.transform import (
    transform_points_from_downsampled_to_atlas_space,
    transform_points_from_raw_to_downsampled_space,
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


@pytest.mark.parametrize(
    "source_image_plane," "orientation," "expected_transformed_points,",
    [
        (np.ones((100, 100, 100)), "asr", [[10, 5, 5], [12, 6, 6]]),
        (np.ones((100, 100, 100)), "psr", [[40, 5, 5], [38, 6, 6]]),
        (Path.home() / "test.tiff", "asr", [[10, 5, 5], [12, 6, 6]]),
        (Path.home() / "test", "psr", [[40, 5, 5], [38, 6, 6]]),
        (str(Path.home() / "test.tiff"), "asr", [[10, 5, 5], [12, 6, 6]]),
        (str(Path.home() / "test"), "psr", [[40, 5, 5], [38, 6, 6]]),
    ],
)
def test_transform_points_from_raw_to_downsampled_space_array(
    mocker, source_image_plane, orientation, expected_transformed_points
):
    if isinstance(source_image_plane, (str, Path)):
        mocker.patch(
            "brainglobe_utils.brainreg.transform.get_size_image_from_file_paths",
            return_value={"z": 100, "y": 100, "x": 100},
        )

    target_space = bgs.AnatomicalSpace(
        origin="asr",
        resolution=(100, 100, 100),
        shape=(50, 25, 25),
    )

    raw_points = np.array([[20, 20, 20], [24, 24, 24]])
    voxel_sizes = [50, 25, 25]

    transformed_points = transform_points_from_raw_to_downsampled_space(
        raw_points, source_image_plane, orientation, voxel_sizes, target_space
    )

    assert np.all(transformed_points == expected_transformed_points)
