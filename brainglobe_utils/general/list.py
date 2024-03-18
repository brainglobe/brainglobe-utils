from natsort import natsorted


def remove_empty_string(str_list):
    """
    Removes any empty strings from a list of strings

    Parameters
    ----------
    str_list : list of str
        List of strings.

    Returns
    -------
    list of str
        List of strings without the empty strings.
    """
    return list(filter(None, str_list))


def unique_elements_lists(list_in):
    """return the unique elements in a list"""
    return list(dict.fromkeys(list_in))


def check_unique_list(in_list, natural_sort=True):
    """
    Checks if all the items in a list are unique or not.

    Parameters
    ----------
    in_list : list
        Input list.

    natural_sort : bool, optional
        Sort the resulting items naturally. Default is True.

    Returns
    -------
    bool
        True if all items are unique, False otherwise.

    list
        A list of any repeated values.
    """
    unique = set(in_list)
    repeated_items = []

    for item in unique:
        count = in_list.count(item)
        if count > 1:
            repeated_items.append(item)

    if repeated_items:
        if natural_sort:
            repeated_items = natsorted(repeated_items)
        return False, repeated_items
    else:
        return True, []


def common_member(a, b, natural_sort=True):
    """
    Checks if two lists (or sets) have a common member, and if so, returns
    the common members.

    Parameters
    ----------
    a : list or set
        First list (or set).

    b : list or set
        Second list (or set).

    natural_sort : bool, optional
        Sort the resulting items naturally. Default is True.

    Returns
    -------
    bool
        True if common members exist, False otherwise.

    list
        The list of common values.
    """
    a_set = set(a)
    b_set = set(b)
    intersection = list(a_set.intersection(b_set))
    if len(intersection) > 0:
        result = True
    else:
        result = False

    if natural_sort:
        intersection = natsorted(intersection)

    return result, intersection
