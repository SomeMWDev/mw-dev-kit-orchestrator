import yaml

def load_config():
    with open("config.yml", "r") as file:
        return yaml.safe_load(file)

def get_kits(config):
    return config["kits"].items()
