import docker
import docker.errors
from docker import DockerClient
from docker.models.networks import Network


def create_docker_network(docker_client: DockerClient) -> Network:
    try:
        return docker_client.networks.get("mw-orchestrator-net")
    except docker.errors.APIError:
        return docker_client.networks.create("mw-orchestrator-net")
