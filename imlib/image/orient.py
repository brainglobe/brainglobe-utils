import numpy as np


def reorient_image(image, invert_axes=None, orientation="saggital"):
    """
    Reorients the image to the coordinate space of the atlas

    :param image_path: str
    :param threshold: float
    :param invert_axes: tuple (Default value = None)
    :param image:
    :param orientation:  (Default value = "saggital")

    """
    if invert_axes is not None:
        for axis in list(invert_axes):
            image = np.flip(image, axis=axis)

    if orientation is not "saggital":
        if orientation is "coronal":
            transposition = (2, 1, 0)
        elif orientation is "horizontal":
            transposition = (1, 2, 0)

        image = np.transpose(image, transposition)
    return image
