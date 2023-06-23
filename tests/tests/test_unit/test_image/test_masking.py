import numpy as np

import brainglobe_utils.image.masking as masking

raw_image = np.array(
    [
        [1, 1, 3, 3, 1, 1],
        [1, 1, 5, 5, 1, 1],
        [1, 1, 5, 5, 1, 1],
        [1, 1, 5, 5, 1, 1],
    ]
)

mask_val_4 = np.array(
    [
        [0, 0, 0, 0, 0, 0],
        [0, 0, 1, 1, 0, 0],
        [0, 0, 1, 1, 0, 0],
        [0, 0, 1, 1, 0, 0],
    ]
)

masked_image = np.array(
    [
        [0, 0, 0, 0, 0, 0],
        [0, 0, 5, 5, 0, 0],
        [0, 0, 5, 5, 0, 0],
        [0, 0, 5, 5, 0, 0],
    ]
)


def test_make_mask():
    assert (mask_val_4 == masking.make_mask(raw_image, threshold=4)).all()


def test_mask_image_threshold():
    result = masking.mask_image_threshold(raw_image, raw_image, threshold=4)
    assert (result == masked_image).all()
