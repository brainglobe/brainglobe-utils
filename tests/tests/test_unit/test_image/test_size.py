import numpy as np
from imlib.image import size

img = np.array(
    [
        [0, 0, 1, 1, 0],
        [0, 10, 100, 10, 0],
        [0, 1, 10, 1, 0],
    ]
)

resized_test = np.array(
    [
        [0, 0, 0, 1, 1, 1, 1, 0, 0],
        [0, 0, 0, 1, 1, 1, 1, 0, 0],
        [0, 0, 0, 1, 1, 1, 1, 0, 0],
        [0, 10, 10, 100, 100, 10, 10, 0, 0],
        [0, 10, 10, 100, 100, 10, 10, 0, 0],
        [0, 10, 10, 100, 100, 10, 10, 0, 0],
        [0, 10, 10, 100, 100, 10, 10, 0, 0],
        [0, 1, 1, 10, 10, 1, 1, 0, 0],
        [0, 1, 1, 10, 10, 1, 1, 0, 0],
        [0, 1, 1, 10, 10, 1, 1, 0, 0],
    ]
)


def test_resize_array():
    target_size = (10, 9)
    resized_image = size.resize_array(img, target_size)
    assert (resized_image == resized_test).all()
