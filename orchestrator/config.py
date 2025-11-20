import yaml

from orchestrator.models import MWDevKit


def load_config():
    with open("config.yml", "r") as file:
        return yaml.safe_load(file)

def load_kits(config) -> dict[str, MWDevKit]:
    kits = {}
    for kit_name, data in config["kits"].items():
        kits[kit_name] = MWDevKit(
            name=kit_name,
            domain=data.get("domain"),
            port=data.get("port", 80),
            web_container=data.get("web-container", f"{kit_name}-mediawiki-web-1"),
            connect_initially=data.get("connect-initially", False)
        )
    return kits
