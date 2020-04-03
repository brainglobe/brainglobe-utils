import random
from imlib.plotting.seaborn import get_seaborn_hex


def get_random_colors(number_of_colors):
    """
    Get a number of random colours as hex
    """
    colors = [
        "#" + "".join([random.choice("0123456789ABCDEF") for j in range(6)])
        for i in range(number_of_colors)
    ]
    return colors


def get_n_colors(object_list=[], override_number=None, palette="husl"):
    """
    Given a list of objects, return a list of colors (based on a seaborn
    palette) of the same length

    :param object_list: List of objects. len(object_list) is the number of
    colors that will be returned
    :param override_number: To return a specific number of colors, set this
    instead
    :param palette: seaborn palette
    """

    if override_number is not None:
        num_colors = override_number
    else:
        num_colors = len(object_list)
    colors = get_seaborn_hex(palette=palette, num=num_colors)
    return colors
