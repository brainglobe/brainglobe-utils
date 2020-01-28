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
