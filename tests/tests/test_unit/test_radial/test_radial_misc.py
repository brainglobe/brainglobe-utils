import pytest
import numpy as np

from imlib.radial import misc

pi = np.pi


def test_opposite_angle():
    assert 180 == misc.opposite_angle(360)
    assert 360 == misc.opposite_angle(180)
    assert 180 == misc.opposite_angle(0)
    assert 90 == misc.opposite_angle(270)
    assert 270 == misc.opposite_angle(90)
    assert 45 == misc.opposite_angle(225)
    assert 10 == misc.opposite_angle(190)
    assert 55 == misc.opposite_angle(235)
    assert 170 == misc.opposite_angle(350)
    assert 250 == misc.opposite_angle(70)

    assert pi == pytest.approx(misc.opposite_angle(0, degrees=False))
    assert 2 * pi == pytest.approx(misc.opposite_angle(pi, degrees=False))
    assert pi / 4 == pytest.approx(
        misc.opposite_angle((5 * pi) / 4, degrees=False)
    )
    assert 1.1 * pi == pytest.approx(
        misc.opposite_angle(0.1 * pi, degrees=False)
    )


def test_radial_bins():
    assert np.array(
        [
            0,
            25,
            50,
            75,
            100,
            125,
            150,
            175,
            200,
            225,
            250,
            275,
            300,
            325,
            350,
            375,
        ]
    ) == pytest.approx(misc.radial_bins(25))
    assert np.array(
        [
            0,
            25,
            50,
            75,
            100,
            125,
            150,
            175,
            200,
            225,
            250,
            275,
            300,
            325,
            350,
        ]
    ) == pytest.approx(misc.radial_bins(25, remove_greater_than_360=True))

    assert np.array([0, 3.45575192, 6.91150384]) == pytest.approx(
        misc.radial_bins(1.1 * np.pi, degrees=False)
    )
    assert np.array([0, 3.45575192]) == pytest.approx(
        misc.radial_bins(
            1.1 * np.pi, degrees=False, remove_greater_than_360=True
        )
    )
