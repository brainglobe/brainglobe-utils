from configobj import ConfigObj


def get_config_obj(config_path):
    config_path = str(config_path)
    config_obj = ConfigObj(config_path, encoding="UTF8", indent_type="    ",)
    return config_obj
