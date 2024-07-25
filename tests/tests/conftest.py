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
        path=Path.home() / ".brainglobe" / "test_data",
        base_url="https://gin.g-node.org/BrainGlobe/test-data/raw/master/",
        registry={
            "cellfinder/cells-z-1000-1050.xml": None,
            "cellfinder/other-cells-z-1000-1050.xml": None,
            "brainglobe-utils/points_transform_brainreg_directory.zip": "a1997f61a5efa752584ea91b7c479506343215bb91f5be09a72349f24e21fc54",  # noqa: E501
        },
    )
    return registry
