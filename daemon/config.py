from configparser import ConfigParser
import os

CONFIG_PATH = "config.ini"
config = ConfigParser()


def load_config():
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
    for category in defaults:
        if category in config:
            has_category = category in config
            for key in defaults[category]:
                if has_category:
                    if not (key in config[category]):
                        config[category][key] = defaults[category][key]
                        rewrite = True
        else:
            config[category] = defaults[category]
            rewrite = True

    # Update the config file if necessary
    if rewrite:
        print("Writing config file")
        with open(CONFIG_PATH, 'w') as configfile:
            config.write(configfile)

    return config
