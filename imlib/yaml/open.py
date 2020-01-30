import yaml


def read_yaml_section(yaml_file, section):
    yaml_contents = open_yaml(yaml_file)
    contents = yaml_contents[section]
    return contents


def open_yaml(arg_file):
    with open(arg_file) as af:
        yaml_args = yaml.load(af, Loader=yaml.FullLoader)
    return yaml_args
