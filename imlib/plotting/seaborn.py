import seaborn as sns


def get_seaborn_hex(palette="husl", num=10):
    """
    Given a seaborn palette, return num colors as hex
    """
    pal = sns.color_palette(palette, num)
    return pal.as_hex()
