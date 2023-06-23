import operator


def check_none(*args):
    """
    Checks if any of the arguments are None
    :param args: A list of objects of any time
    :return: True if any of the arguments are None
    """
    if any(arg is None for arg in args):
        return True
    else:
        return False


def convert_string_to_operation(string_operation, inclusive=True):
    """
    Converts a string (e.g. "higher") to an operation (e.g. operator.ge)
    :param str string_operation: Operation as a string, e.g. "lower than"
    :param inclusive: If True, the operation will be inclusive, i.e. ">="
    rather than ">"
    :return:
    """
    equal_list = ["equal", "same"]
    lower_list = [
        "lower",
        "low",
        "less",
        "less than",
        "lessthan",
        "less_than",
        "lower than",
    ]
    higher_list = [
        "higher",
        "high",
        "higher",
        "more" "more than",
        "morethan",
        "more_than",
        "higher than",
    ]

    if string_operation in equal_list:
        operation = operator.eq
    elif string_operation in lower_list:
        if inclusive:
            operation = operator.le
        else:
            operation = operator.lt
    elif string_operation in higher_list:
        if inclusive:
            operation = operator.ge
        else:
            operation = operator.gt
    else:
        raise NotImplementedError(
            "convert_string_to_operation is only implemented for "
            "equal conditions: {}, lower conditions: {} and higher conditions:"
            '{}. Condition: "{}" is not recognised.'.format(
                equal_list, lower_list, higher_list, string_operation
            )
        )
    return operation
