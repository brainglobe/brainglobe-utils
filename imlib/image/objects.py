import numpy as np
from skimage.measure import label


def get_largest_non_zero_object(label_image):
    """
    In a labelled (each object assigned an int) numpy array. Return the
    largest object with a value >= 1.
    :param label_image: Output of skimage.measure.label
    :return: Boolean numpy array or largest object
    """
    return label_image == np.argmax(np.bincount(label_image.flat)[1:]) + 1


def keep_n_largest_objects(numpy_array, n=1, connectivity=None):
    """
    Given an input binary numpy array, return a "clean" array with only the
    n largest connected components remaining

    Inspired by stackoverflow.com/questions/47540926

    TODO: optimise

    :param numpy_array: Binary numpy array
    :param n: How many objects to keep
    :param connectivity: Labelling connectivity (see skimage.measure.label)
    :return: "Clean" numpy array with n largest objects
    """

    labels = label(numpy_array, connectivity=connectivity)
    assert labels.max() != 0  # assume at least 1 CC
    n_largest_objects = get_largest_non_zero_object(labels)
    if n > 1:
        i = 1
        while i < n:
            labels[n_largest_objects] = 0
            n_largest_objects += get_largest_non_zero_object(labels)
            i += 1
    return n_largest_objects
