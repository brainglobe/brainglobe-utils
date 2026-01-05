import random
from argparse import ArgumentTypeError
from random import randint

import pytest

from brainglobe_utils.general import numerical


def test_is_even():
    even_number = random.randrange(2, 1000, 2)
    odd_number = random.randrange(1, 1001, 2)
    with pytest.raises(NotImplementedError):
        assert numerical.is_even(0)
    assert numerical.is_even(even_number)
    assert not numerical.is_even(odd_number)


def test_check_positive_float():
    pos_val = randint(1, 1000) / 100
    neg_val = -randint(1, 1000) / 100

    assert pos_val == numerical.check_positive_float(pos_val)

    with pytest.raises(ArgumentTypeError):
        assert numerical.check_positive_float(neg_val)

    for none_val in [None, "None", "none"]:
        assert numerical.check_positive_float(none_val) is None
        with pytest.raises(ArgumentTypeError):
            assert numerical.check_positive_float(none_val, none_allowed=False)

    assert numerical.check_positive_float(0) == 0


def test_check_positive_int():
    pos_val = randint(1, 1000)
    neg_val = -randint(1, 1000)

    assert pos_val == numerical.check_positive_int(pos_val)

    with pytest.raises(ArgumentTypeError):
        assert numerical.check_positive_int(neg_val)

    for none_val in [None, "None", "none"]:
        assert numerical.check_positive_int(none_val) is None
        with pytest.raises(ArgumentTypeError):
            assert numerical.check_positive_int(none_val, none_allowed=False)

    assert numerical.check_positive_int(0) == 0
