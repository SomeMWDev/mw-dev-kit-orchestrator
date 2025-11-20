import docker
from fastapi import FastAPI, Response, status

from orchestrator.config import load_config
from orchestrator.nginx import get_networks

app = FastAPI()
config = load_config()

initialized_networks = False

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

initialized_networks = True

@app.get("/health")
async def health():
    if not initialized_networks:
        return Response(
            content='{"status": "initializing"}',
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            media_type="application/json",
        )
    # TODO only return after initializing networks
    return {"status": "ok"}
