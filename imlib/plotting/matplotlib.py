from matplotlib.patches import Patch


def make_legend(names, colors):
    """

    Make a list of legend handles and colours
    :param names: list of names
    :param colors: list of colors
    :return: list of matplotlib.patches.Patch objects for legend
    """
    legend_elements = []
    for idx, name in enumerate(names):
        el = Patch(color=colors[idx], label=name)
        legend_elements.append(el)
    return legend_elements
