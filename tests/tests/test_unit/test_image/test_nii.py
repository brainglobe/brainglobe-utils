import numpy as np
from pathlib import Path

from imlib.image import nii


data_dir = Path("tests", "data")
config_file = data_dir / "nii" / "conf.conf"

atlas_pixel_sizes = {"x": "10", "y": "10", "z": "10"}
transformation_matrix = np.array(
    ([10, 0, 0, 0], [0, 10, 0, 0], [0, 0, 10, 0], [0, 0, 0, 1])
)


def test_get_atlas_pixel_sizes():
    assert nii.get_atlas_pixel_sizes(config_file) == atlas_pixel_sizes


def test_get_transformation_matrix():
    test_transformation_matrix = nii.get_transformation_matrix(config_file)
    assert (test_transformation_matrix == transformation_matrix).all()
