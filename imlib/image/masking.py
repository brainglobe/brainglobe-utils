import numpy as np


def mask_image_threshold(image, masking_image, threshold=0):
    """
    Mask one image, based on the values in another image that are above a
    threshold
    :param image: Input image
    :param masking_image: Image to base the mask on (same shape as image)
    :param threshold: Threshold to base the mask on
    :return: Masked image
    """
    masking_image = make_mask(masking_image, threshold=threshold)
    return image * masking_image


def make_mask(masking_image, threshold=0):
    """
    Given an image, and an optional threshold, returns a binary image that can
    be used as a mask
    :param masking_image: nD image
    :param threshold: Optional threshold, default 0. Values above this are
    included in the mask. Values below this are not.
    :return: Binary mask
    """
    mask = np.copy(masking_image)
    mask[masking_image <= threshold] = 0
    mask[masking_image > threshold] = 1
    return mask
