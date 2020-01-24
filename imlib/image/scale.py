import numpy as np


def scale_to_16_bits(img):
    """
    Normalise the input image to the full 0-2^16 bit depth.

    :param np.array img: The input image
    :return: The normalised image
    :rtype: np.array
    """
    normalised = img / img.max()
    return normalised * (2 ** 16 - 1)


def scale_and_convert_to_16_bits(img):
    """
    Normalise the input image to the full 0-2^16 bit depth, and return as
    type: "np.uint16".

    :param np.array img: The input image
    :return: The normalised, 16 bit image
    :rtype: np.array
    """
    img = scale_to_16_bits(img)
    return img.astype(np.uint16, copy=False)
