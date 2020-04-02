def remove_empty_string(str_list):
    """
    Removes any empty strings from a list of strings
    :param str_list: List of strings
    :return: List of strings without the empty strings
    """
    return list(filter(None, str_list))


def unique_elements_lists(list_in):
    """ return the unique elements in a list"""
    return list(dict.fromkeys(list_in))


def strip_spaces_list(list_in, strip_method="all"):
    """
    Remove spaces from all items in a list
    :param list_in:
    :param strip_method: Default: 'all' for leading and trailing spaces.
    Can also be 'leading' or 'trailing'
    :return: List with items stripped of spaces
    """

    if strip_method == "all":
        list_out = [item.strip() for item in list_in]
    elif strip_method == "leading":
        list_out = [item.rstrip() for item in list_in]
    elif strip_method == "trailing":
        list_out = [item.lstrip() for item in list_in]
    else:
        raise NotImplementedError(
            'Strip method: "{}" is not implemented. Please use "all", '
            '"leading" or "trailing"'.format(strip_method)
        )
    return list_out


def split_list(input_list):
    """
    Splits a list in half (assumes even length)
    :param input_list:
    :return: Tuple of the first and second halves of the list
    """
    if len(input_list) % 2 == 0:
        half = len(input_list) // 2
        return input_list[:half], input_list[half:]
    else:
        raise NotImplementedError("split_list requires a list of even length")
