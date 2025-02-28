"""Handles IO of config file."""

from configparser import ConfigParser
import os

CONFIG_PATH = "config.ini"
config = ConfigParser()


def load_config():
    """
    Reads config from `CONFIG_PATH`
    If doesn't exist, creates the file with default values.
    """
    # Default values
    defaults = {
        'DATABASE': {
            'DB_ENABLED': 'False',
            'DB_USER': 'username',
            'DB_PASSWORD': 'password',
            'DB_DATABASE': 'database_name',
            'DB_HOST': "hostname/ip",
        }
    }

    # Load values if file exists
    if os.path.exists(CONFIG_PATH):
        print("Reading config file")
        config.read(CONFIG_PATH)
    rewrite = False

    # Fill in missing details
    for category, items in defaults.items():
        if category in config:
            has_category = category in config
            for key in items:
                if has_category:
                    if key not in config[category]:
                        config[category][key] = defaults[category][key]
                        rewrite = True
        else:
            config[category] = defaults[category]
            rewrite = True

    # Update the config file if necessary
    if rewrite:
        print("Writing config file")
        with open(CONFIG_PATH, 'w', encoding="utf-8") as configfile:
            config.write(configfile)

    return config
