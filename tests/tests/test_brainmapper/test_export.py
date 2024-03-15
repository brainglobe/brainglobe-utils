import numpy as np
import pytest

from brainglobe_utils.brainmapper.export import export_points_to_brainrender


@pytest.fixture
def points():
    return np.reshape(np.arange(0, 12), (4, 3))


def test_export_brainrender(tmp_path, points):
    """
    Test that a .npy file can be saved with correct resolution
    """
    resolution = 100
    save_path = tmp_path / "points.npy"
    export_points_to_brainrender(points, resolution, save_path)

    reloaded = np.load(save_path)
    assert (reloaded == points * resolution).all()
