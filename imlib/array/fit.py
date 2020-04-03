import numpy as np


def polyfit_curve(x, y, fit_degree=1):
    """
    Calculates the curve of best fit, to a given polynomial degree, for given
    points in x & y.
    :param x: Input points
    :param y: Input points
    :param fit_degree: Degree of the fitting polynomial
    :return: 1D fitted curve
    """
    poly_fit = np.polyfit(x, y, fit_degree)
    return np.polyval(poly_fit, x)


def max_polyfit(x, y, fit_degree=1):
    """
    Calculates the max value of a series of points, based on a polynomial fit.
    Should reduce the effect of outliers.
    :param np.array x: Input points
    :param np.array y: Input points
    :param int fit_degree: Degree of the fitting polynomial
    :return: Maximum value of the curve.
    """
    if x.ndim > 1 or y.ndim > 1:
        raise NotImplementedError(
            "max_polyfit only works for 1D arrays. "
            "x has {} dimensions and y has {}.".format(x.ndim, y.ndim)
        )
    if len(x) != len(y):
        raise ValueError(
            "x and y must be the same length. x has length: {}, "
            "and y has length: {}".format(len(x), len(y))
        )

    curve = polyfit_curve(x, y, fit_degree=fit_degree)
    return curve.max()
