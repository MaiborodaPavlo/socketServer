import configparser
import os

PATH = 'settings.ini'


def create_config(path):
    """
    Create a config file
    """
    config = configparser.ConfigParser()
    config.add_section("Settings")
    config.set("Settings", "short_log", "0")
    config.set("Settings", "show_errors", "0")
    config.set("Settings", "bg_color", "white")
    config.add_section("Connection")
    config.set("Connection", "host", "127.0.0.1")
    config.set("Connection", "port", "8000")

    with open(path, "w") as config_file:
        config.write(config_file)


def get_config(path):
    """
    Returns the config object
    """
    if not os.path.exists(path):
        create_config(path)

    config = configparser.ConfigParser()
    config.read(path)
    return config


def get_setting(path, section, setting):
    """
    return a setting
    """
    config = get_config(path)
    value = config.get(section, setting)

    return value


def update_setting(path, section, setting, value):
    """
    Update a setting
    """
    config = get_config(path)
    config.set(section, setting, value)

    with open(path, "w") as config_file:
        config.write(config_file)


def delete_setting(path, section, setting):
    """
    Delete a setting
    """
    config = get_config(path)
    config.remove_option(section, setting)

    with open(path, "w") as config_file:
        config.write(config_file)
