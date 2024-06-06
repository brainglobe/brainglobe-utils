from pathlib import Path

import pooch
import pytest


@pytest.fixture
def data_path():
    """Directory storing all test data"""
    return Path(__file__).parent.parent / "data"


@pytest.fixture
def test_data_registry():
    """
    Create a test data registry for BrainGlobe.

    Returns:
        pooch.Pooch: The test data registry object.

    """
    registry = pooch.create(
        path=pooch.os_cache("brainglobe_test_data"),
        base_url="https://gin.g-node.org/BrainGlobe/test-data/raw/master/",
        registry={
            "cellfinder/cells-z-1000-1050.xml": None,
            "cellfinder/other-cells-z-1000-1050.xml": None,
        },
        env="BRAINGLOBE_TEST_DATA_DIR",
    )
    return registry
