import numpy as np


def scale_to_16_bits(img):
    """
    Normalise the input image to the full 0-2^16 bit depth.

    Parameters
    ----------
    img : np.ndarray
        The input image

    Returns
    -------
    np.ndarray
        The normalised image
    """
    normalised = img / img.max()
    return normalised * (2**16 - 1)


def scale_and_convert_to_16_bits(img):
    """
    Normalise the input image to the full 0-2^16 bit depth, and return as
    type: "np.uint16".

    Parameters
    ----------
    img : np.ndarray
        The input image

    Returns
    -------
    np.ndarray
        The normalised, 16 bit image
    """
    img = scale_to_16_bits(img)
    return img.astype(np.uint16, copy=False)
