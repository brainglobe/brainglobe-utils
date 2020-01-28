def convert_shape_dict_to_array_shape(shape_dict, type="numpy"):
    """
    Converts a dict with "x", "y" (and optionally "z") attributes into
    a tuple that can be used to e.g. initialise a numpy array
    :param shape_dict: Dict with  "x", "y" (and optionally "z") attributes
    :param type: One of "numpy" or "fiji", to determine whether the "x" or the
    "y" attribute is the first dimension.
    :return: Tuple array shape
    """

    shape = []
    if type is "numpy":
        shape.append(int(shape_dict["y"]))
        shape.append(int(shape_dict["x"]))

    elif type is "fiji":
        shape.append(int(shape_dict["x"]))
        shape.append(int(shape_dict["y"]))
    else:
        raise NotImplementedError(
            "Type: {} not recognise, please specify "
            "'numpy' or 'fiji'".format(type)
        )
    if "z" in shape_dict:
        shape.append(int(shape_dict["z"]))

    return tuple(shape)
