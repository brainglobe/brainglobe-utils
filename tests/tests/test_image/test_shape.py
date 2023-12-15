import pytest

from brainglobe_utils.image.shape import convert_shape_dict_to_array_shape


def test_convert_shape_dict_to_array_shape():
    shape_dict = {"x": "100", "y": "30"}
    assert convert_shape_dict_to_array_shape(shape_dict) == (30, 100)
    assert convert_shape_dict_to_array_shape(shape_dict, type="fiji") == (
        100,
        30,
    )

    shape_dict["z"] = 10
    assert convert_shape_dict_to_array_shape(shape_dict) == (30, 100, 10)

    with pytest.raises(NotImplementedError):
        convert_shape_dict_to_array_shape(shape_dict, type="new type")
