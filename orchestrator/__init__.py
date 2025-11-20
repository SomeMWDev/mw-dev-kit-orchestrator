from contextlib import asynccontextmanager

import docker
import docker.errors
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from orchestrator.config import load_config
from orchestrator.nginx import regenerate_nginx_config


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.config = load_config()
    app.docker_client = docker.from_env()
    try:
        app.docker_network = app.docker_client.networks.get("mw-orchestrator-net")
    except docker.errors.APIError:
        app.docker_network = app.docker_client.networks.create("mw-orchestrator-net")

    app.nginx_container = app.docker_client.containers.get("mw-orchestrator-nginx")
    app.docker_network.connect(app.nginx_container)
    regenerate_nginx_config(app.config, app.docker_client, app.docker_network, app.nginx_container, reload=False)

    yield

app = FastAPI(lifespan=lifespan)

@app.get("/health")
async def health():
    return {"status": "ok"}


app.mount("/", StaticFiles(directory="orchestrator/static"), name="static")
