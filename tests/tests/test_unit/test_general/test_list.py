from imlib.general import list as list_tools

list_with_empty = ["test1", "test 2", " ", "", "test4", ""]

list_without_empty = ["test1", "test 2", " ", "test4"]


def test_remove_empty_string():
    assert (
        list_tools.remove_empty_string(list_with_empty) == list_without_empty
    )


def test_unique_elements_list():
    list_in = [1, 2, 2, "a", "b", 1, "a", "dog"]
    unique_list = [1, 2, "a", "b", "dog"]
    assert list_tools.unique_elements_lists(list_in) == unique_list
