import yaml

path_to_config = r'C:\Users\orlan\PycharmProjects\config.yaml'  # Конфиг с паролями и токеном


def get_config():
    with open(path_to_config) as f:
        return yaml.safe_load(f)


CONFIG = get_config()

log = CONFIG["log"]
sasha1 = CONFIG["sasha1"]
admin = CONFIG["admin"]
TOKEN = CONFIG["TOKEN"]
