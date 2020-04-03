import numpy as np


def calculate_gradient_1d(array):
    """
    Calculates the first order gradient of a given array
    :param array: 1D numpy array
    :return: gradient of the array
    """
    x = range(1, len(array) + 1)
    gradient, _ = np.polyfit(x, array, 1)
    return gradient


def multiply_across(array, column_vector):
    """
    Multiplies a column vector across a 2D array
    :param array: 2D numpy array
    :param column_vector: column vector
    :return: numpy array
    """

    return array * column_vector[:, np.newaxis]
