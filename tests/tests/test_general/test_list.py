import pytest

from brainglobe_utils.general import list as list_tools


@pytest.mark.parametrize(
    "list_with_empty, list_without_empty",
    [
        pytest.param(
            ["test1", "test 2", " ", "", "test4", ""],
            ["test1", "test 2", " ", "test4"],
            id="remove empty string",
        ),
    ],
)
def test_remove_empty_string(list_with_empty, list_without_empty):
    assert (
        list_tools.remove_empty_string(list_with_empty) == list_without_empty
    )


def test_unique_elements_list():
    list_in = [1, 2, 2, "a", "b", 1, "a", "dog"]
    unique_list = [1, 2, "a", "b", "dog"]
    assert list_tools.unique_elements_lists(list_in) == unique_list


def test_check_unique_list():
    a = [1, "a", 10, 30]
    assert (True, []) == list_tools.check_unique_list(a)
    repeating_list = [1, 2, 3, 3, "dog", "cat", "dog"]
    assert (False, [3, "dog"]) == list_tools.check_unique_list(repeating_list)


@pytest.mark.parametrize(
    "a, b",
    [
        pytest.param([1, "a", 10, 30], [30, 10, "c", "d"], id="common 10 30"),
    ],
)
def test_common_member(a, b):
    assert (True, [10, 30]) == list_tools.common_member(a, b)
