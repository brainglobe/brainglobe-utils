from argparse import ArgumentTypeError

import pytest

from brainglobe_utils.general import string


@pytest.fixture
def jabberwocky(data_path):
    return data_path / "general" / "jabberwocky.txt"


@pytest.fixture
def jabberwocky_list():
    return [
        "’Twas brillig, and the slithy toves",
        "Did gyre and gimble in the wabe:",
        "All mimsy were the borogoves,",
        "And the mome raths outgrabe.",
        "“Beware the Jabberwock, my son!",
        "The jaws that bite, the claws that catch!",
        "Beware the Jubjub bird, and shun",
        "The frumious Bandersnatch!”",
        "He took his vorpal sword in hand;",
        "Long time the manxome foe he sought—",
        "So rested he by the Tumtum tree",
        "And stood awhile in thought.",
        "And, as in uffish thought he stood,",
        "The Jabberwock, with eyes of flame,",
        "Came whiffling through the tulgey wood,",
        "And burbled as it came!",
        "One, two! One, two! And through and through",
        "The vorpal blade went snicker-snack!",
        "He left it dead, and with its head",
        "He went galumphing back.",
        "“And hast thou slain the Jabberwock?",
        "Come to my arms, my beamish boy!",
        "O frabjous day! Callooh! Callay!”",
        "He chortled in his joy.",
        "’Twas brillig, and the slithy toves",
        "Did gyre and gimble in the wabe:",
        "All mimsy were the borogoves,",
        "And the mome raths outgrabe.",
    ]


def test_get_string_lines(jabberwocky, jabberwocky_list):
    assert string.get_text_lines(jabberwocky) == jabberwocky_list
    assert (
        string.get_text_lines(jabberwocky, return_lines=8)
        == jabberwocky_list[8]
    )


def test_check_str():
    assert "me" == string.check_str("me")
    assert "12" == string.check_str("12")

    for none_val in [None, "None", "none"]:
        assert string.check_str(none_val) is None
        with pytest.raises(ArgumentTypeError):
            assert string.check_str(none_val, none_allowed=False)
