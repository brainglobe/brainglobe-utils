import numpy as np
import pytest
from tifffile import imread

from brainglobe_utils.image.heatmap import heatmap_from_points, rescale_array


@pytest.fixture
def heatmap_validate_path(data_path):
    return data_path / "image" / "heatmap.tif"


@pytest.fixture
def points():
    return np.array([[5, 5, 5], [10, 10, 10], [15, 15, 15]])


@pytest.fixture
def mask_array():
    """
    A simple array of size (20,20,20) where the left side
    is 0 and the right side is 1
    """
    array = np.zeros((20, 20, 20))
    array[:, :, 10:] = 1
    return array


def test_rescale_array(mask_array):
    small_array = np.zeros((10, 10, 10))
    resized_array = rescale_array(mask_array, small_array)
    assert resized_array.shape == small_array.shape


def test_heatmap_from_points(
    tmp_path, mask_array, points, heatmap_validate_path
):
    output_filename = tmp_path / "test_heatmap.tif"

    heatmap_test = heatmap_from_points(
        points,
        2,
        (20, 20, 20),
        bin_sizes=(2, 2, 2),
        output_filename=output_filename,
        smoothing=5,
        mask_image=mask_array,
    )
    heatmap_validate = imread(heatmap_validate_path)
    assert np.array_equal(heatmap_validate, heatmap_test)

    heatmap_file = imread(output_filename)
    assert np.array_equal(heatmap_validate, heatmap_file)
