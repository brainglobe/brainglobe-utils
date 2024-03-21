from pathlib import Path

import pytest


@pytest.fixture
def data_path():
    """Directory storing all test data"""
    return Path(__file__).parent.parent / "data"
