import numpy as np


def sine_min_max(frequency):
    """
    For a given frequency, return the minimum and maximum values that
    correspond to a single full peak (i.e. -1 to -1)
    :param frequency:
    :return: minimum and maximum values (in radians)
    """
    period = 2 * np.pi / frequency
    min_val = -period / 4
    max_val = 3 * period / 4
    return min_val, max_val


def get_scaled_sine(x, y_max, frequency):
    """
    For a given input (x), returns a sine function, scaled to a given maximum
    value.
    :param x: Array of x values
    :param y_max: Target maximum value of the function
    :param frequency:  Sine wave frequency
    :return: Sine function with a given max
    """
    y = np.sin(frequency * x) + 1
    y = y * (y_max / y.max())
    return y
