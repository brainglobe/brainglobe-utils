import pytest
import numpy as np
from imlib.array import misc


def test_midpoints_of_series():
    assert (
        np.array([1, 3, 5, 7, 9])
        == misc.midpoints_of_series(np.array([0, 2, 4, 6, 8, 10]))
    ).all()

    assert (
        np.array([-3, 4.5, 65])
        == misc.midpoints_of_series(np.array([-5, -1, 10, 120]))
    ).all()

    assert np.array([-499.9, 500.1, 50500]) == pytest.approx(
        misc.midpoints_of_series(np.array([-1000, 0.20, 1000, 100000]))
    )
