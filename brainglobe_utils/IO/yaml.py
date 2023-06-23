import yaml


def read_yaml_section(yaml_file, section):
    yaml_contents = open_yaml(yaml_file)
    contents = yaml_contents[section]
    return contents


def open_yaml(yaml_file):
    with open(yaml_file) as f:
        yaml_contents = yaml.load(f, Loader=yaml.FullLoader)
    return yaml_contents


def save_yaml(yaml_contents, output_file, default_flow_style=False):
    with open(output_file, "w") as outfile:
        yaml.dump(
            yaml_contents, outfile, default_flow_style=default_flow_style
        )
