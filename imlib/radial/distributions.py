import numpy as np
from scipy.special import i0


def vonmises_kde(data, kappa, n_bins):
    """
    Generates a Vonmises kernel density estimate (KDE) for a given array
    of angles in radians.
    :param data: Angles in radians
    :param kappa: Vonmises kappa parameter
    :param n_bins: How many bins to generate the distribution over
    :return: Bins, Vonmises kDE
    """
    # from https: // stackoverflow.com / questions / 28839246 /
    # scipy - gaussian - kde - and -circular - data
    bins = np.linspace(-np.pi, np.pi, n_bins)
    x = np.linspace(-np.pi, np.pi, n_bins)
    # integrate vonmises kernels
    kde = np.exp(kappa * np.cos(x[:, None] - data[None, :])).sum(1) / (
        2 * np.pi * i0(kappa)
    )
    kde /= np.trapz(kde, x=bins)
    return bins, kde
