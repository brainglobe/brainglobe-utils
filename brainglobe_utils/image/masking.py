import numpy as np


def mask_image_threshold(image, masking_image, threshold=0):
    """
    Mask one image, based on the values in another image that are above a
    threshold.

    Parameters
    ----------
    image : np.ndarray
        Input image
    masking_image : np.ndarray
        Image to base the mask on (same shape as image)
    threshold : int, optional
        Threshold to base the mask on

    Returns
    -------
    np.ndarray
        Masked image
    """
    masking_image = make_mask(masking_image, threshold=threshold)
    return image * masking_image


def make_mask(masking_image, threshold=0):
    """
    Given an image, and an optional threshold, returns a binary image that can
    be used as a mask.

    Parameters
    ----------
    masking_image : np.ndarray
        nD image
    threshold : int, optional
        Optional threshold, default 0. Values above this are
        included in the mask. Values below this are not.

    Returns
    -------
    np.ndarray
        Binary mask
    """
    mask = np.copy(masking_image)
    mask[masking_image <= threshold] = 0
    mask[masking_image > threshold] = 1
    return mask
