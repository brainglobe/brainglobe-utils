import os

from pkg_resources import resource_filename

from imlib.general.config import get_config_obj


def source_config_cellfinder():
    return resource_filename("cellfinder", "config/cellfinder.conf")


def source_custom_config_cellfinder():
    return resource_filename("cellfinder", "config/cellfinder.conf.custom")


def source_config_amap():
    return resource_filename("amap", "amap.conf")


def source_custom_config_amap():
    return resource_filename("amap", "amap.conf.custom")


def get_structures_path(config=None):
    if config is None:
        config = source_custom_config_amap()

    config_obj = get_config_obj(config)
    atlas_conf = config_obj["atlas"]

    return get_atlas_element_path(atlas_conf, "structures_name")


def get_atlas_element_path(atlas_conf, config_entry_name):
    """
    Get the path to an 'element' of the atlas (i.e. the average brain,
    the atlas, or the hemispheres atlas)
    """

    atlas_folder_name = os.path.expanduser(atlas_conf["base_folder"])
    atlas_element_filename = atlas_conf[config_entry_name]
    return os.path.abspath(
        os.path.normpath(
            os.path.join(atlas_folder_name, atlas_element_filename)
        )
    )
