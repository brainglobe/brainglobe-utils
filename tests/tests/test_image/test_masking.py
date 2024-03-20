import numpy as np
import pytest

import brainglobe_utils.image.masking as masking


@pytest.fixture
def raw_image():
    return np.array(
        [
            [1, 1, 3, 3, 1, 1],
            [1, 1, 5, 5, 1, 1],
            [1, 1, 5, 5, 1, 1],
            [1, 1, 5, 5, 1, 1],
        ]
    )


@pytest.fixture
def mask_val_4():
    return np.array(
        [
            [0, 0, 0, 0, 0, 0],
            [0, 0, 1, 1, 0, 0],
            [0, 0, 1, 1, 0, 0],
            [0, 0, 1, 1, 0, 0],
        ]
    )


@pytest.fixture
def masked_image():
    return np.array(
        [
            [0, 0, 0, 0, 0, 0],
            [0, 0, 5, 5, 0, 0],
            [0, 0, 5, 5, 0, 0],
            [0, 0, 5, 5, 0, 0],
        ]
    )


def test_make_mask(mask_val_4, raw_image):
    assert (mask_val_4 == masking.make_mask(raw_image, threshold=4)).all()


def test_mask_image_threshold(raw_image, masked_image):
    result = masking.mask_image_threshold(raw_image, raw_image, threshold=4)
    assert (result == masked_image).all()
