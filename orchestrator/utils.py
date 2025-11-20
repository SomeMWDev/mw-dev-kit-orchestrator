import docker

from orchestrator import get_networks


def initialize_networks(config):
    networks = get_networks(config)
    client = docker.from_env()
    containers = [
        "mw-orchestrator",
        "mw-orchestrator-nginx"
    ]
    for container in containers:
        container = client.containers.get(container)
        for network in networks:
            print(f"Connecting container {container} to network {network}")
            try:
                net = client.networks.get(network)
                net.connect(container)
                print(f"Connected to network {network}")
            except Exception as e:
                print(f"Error connecting to network {network}: {e}")
