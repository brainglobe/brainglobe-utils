import numpy as np
from imlib.general import config


def get_atlas_pixel_sizes(atlas_config_path):
    config_obj = config.get_config_obj(atlas_config_path)
    atlas_conf = config_obj["atlas"]
    atlas_pixel_sizes = atlas_conf["pixel_size"]
    return atlas_pixel_sizes


def get_transformation_matrix(atlas_config=None, pixel_sizes=None):
    """
    From an atlas config, return transformation_matrix for proper nifti output
    :param atlas_config:
    :return: transformation_matrix
    """
    if pixel_sizes is None:
        atlas_pixel_sizes = get_atlas_pixel_sizes(atlas_config)
    else:
        atlas_pixel_sizes = pixel_sizes
    transformation_matrix = np.eye(4)
    for i, axis in enumerate(("x", "y", "z")):
        transformation_matrix[i, i] = atlas_pixel_sizes[axis]
    return transformation_matrix
