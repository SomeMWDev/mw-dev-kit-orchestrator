from docker import DockerClient

from orchestrator.nginx import get_networks


def initialize_networks(config, docker_client: DockerClient):
    networks = get_networks(config)
    containers = [
        "mw-orchestrator",
        "mw-orchestrator-nginx"
    ]
    for container in containers:
        container = docker_client.containers.get(container)
        for network in networks:
            print(f"Connecting container {container} to network {network}")
            try:
                net = docker_client.networks.get(network)
                net.connect(container)
                print(f"Connected to network {network}")
            except Exception as e:
                print(f"Error connecting to network {network}: {e}")
