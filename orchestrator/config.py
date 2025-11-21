import docker.errors
import yaml
from docker import DockerClient

from orchestrator.models import MWDevKit, KitStatus


def load_config():
    with open("config.yml", "r") as file:
        return yaml.safe_load(file)

def load_kits(config, docker_client: DockerClient) -> dict[str, MWDevKit]:
    kits = {}
    for kit_name, data in config["kits"].items():
        web_container = data.get("web-container", f"{kit_name}-mediawiki-web-1")
        try:
            status = KitStatus(docker_client.containers.get(web_container).status)
            print(f"Web container {web_container} is {status}")
        except docker.errors.NotFound:
            print(f"Web container {web_container} not found")
            status = KitStatus.UNKNOWN
        kits[kit_name] = MWDevKit(
            name=kit_name,
            domain=data.get("domain"),
            port=data.get("port", 80),
            web_container=web_container,
            connect_initially=data.get("connect-initially", False),
            status=status,
        )
    return kits
