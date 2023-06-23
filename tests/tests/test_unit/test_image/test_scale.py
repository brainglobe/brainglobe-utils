import numpy as np

from imlib.image import scale

test_2d_img = np.array([[1, 2, 10, 100], [5, 25, 300, 1000], [1, 0, 0, 125]])
validate_2d_img = np.array(
    [
        [65.535, 131.07, 655.35, 6553.5],
        [327.675, 1638.375, 19660.5, 65535],
        [65.535, 0, 0, 8191.875],
    ]
)


def test_scale_to_16_bits():
    validate_2d_img_uint16 = validate_2d_img.astype(np.uint16, copy=False)
    assert (
        validate_2d_img_uint16
        == scale.scale_and_convert_to_16_bits(test_2d_img)
    ).all()
