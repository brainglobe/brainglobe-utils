from pathlib import Path
from imlib.yaml import open

data_dir = Path("tests", "data")
yaml_file = data_dir / "yaml" / "single_section.yml"

yaml_section = [
    {"a": "/some_path", "b": "Eeyore", "d": "a_single_dog", "e": 2},
    {"a": "/another/path", "z": 1, 2: 2},
]

yaml_contents = {"data": yaml_section}


def test_open_yaml():
    yaml_contents_test = open.open_yaml(yaml_file)
    assert yaml_contents_test == yaml_contents


def test_read_yaml_section(section="data"):
    yaml_section_test = open.read_yaml_section(yaml_file, section)
    assert yaml_section_test == yaml_section
