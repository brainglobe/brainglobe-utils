from pathlib import Path

import pytest

from brainglobe_utils.IO import yaml


@pytest.fixture
def yaml_file(data_path):
    return data_path / "yaml" / "single_section.yml"


@pytest.fixture
def yaml_section():
    return [
        {"a": "/some_path", "b": "Eeyore", "d": "a_single_dog", "e": 2},
        {"a": "/another/path", "z": 1, 2: 2},
    ]


@pytest.fixture
def yaml_contents(yaml_section):
    return {"data": yaml_section}


def test_open_yaml(yaml_file, yaml_contents):
    yaml_contents_test = yaml.open_yaml(yaml_file)
    assert yaml_contents_test == yaml_contents


def test_read_yaml_section(yaml_file, yaml_section, section="data"):
    yaml_section_test = yaml.read_yaml_section(yaml_file, section)
    assert yaml_section_test == yaml_section


def test_save_yaml(tmpdir, yaml_file, yaml_contents):
    test_yaml_path = Path(tmpdir) / "test.yml"
    yaml.save_yaml(yaml_contents, test_yaml_path)
    test_yaml = yaml.open_yaml(test_yaml_path)
    saved_yaml = yaml.open_yaml(yaml_file)
    assert test_yaml == saved_yaml
