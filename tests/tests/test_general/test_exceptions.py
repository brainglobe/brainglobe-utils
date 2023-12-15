import pytest

from brainglobe_utils.general.exceptions import CommandLineInputError


def raise_CommandLineInputError():
    raise CommandLineInputError("Error")


def test_CommandLineInputError():
    with pytest.raises(CommandLineInputError) as e:
        raise_CommandLineInputError()
    assert str(e.value) == "Error"
