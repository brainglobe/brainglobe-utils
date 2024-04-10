import yaml


def read_yaml_section(yaml_file, section):
    """
    Read section from yaml file.

    Parameters
    ----------
    yaml_file : str or pathlib.Path
        Path of .yml file to read.
    section : str
        Key of yaml section to read.

    Returns
    -------
    The contents of the yaml section.
    """
    yaml_contents = open_yaml(yaml_file)
    contents = yaml_contents[section]
    return contents


def open_yaml(yaml_file):
    """
    Read the contents of a yaml file.

    Parameters
    ----------
    yaml_file : str or pathlib.Path
        Path of .yml file to read.

    Returns
    -------
    dict
        The contents of the yaml file.
    """
    with open(yaml_file) as f:
        yaml_contents = yaml.load(f, Loader=yaml.FullLoader)
    return yaml_contents


def save_yaml(yaml_contents, output_file, default_flow_style=False):
    """
    Save contents to a yaml file.

    Parameters
    ----------
    yaml_contents : dict
        Content to write to yaml file.
    output_file : str or pathlib.Path
        Path to .yml file to write to.
    default_flow_style : bool, optional
        If true, will use block style or flow style depending on whether there
        are nested collections. If false, always uses block style.
    """
    with open(output_file, "w") as outfile:
        yaml.dump(
            yaml_contents, outfile, default_flow_style=default_flow_style
        )
