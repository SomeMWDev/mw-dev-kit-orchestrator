from contextlib import asynccontextmanager

import docker
import docker.errors
from fastapi import FastAPI
from starlette.requests import Request
from starlette.staticfiles import StaticFiles

from orchestrator.config import load_config, load_kits
from orchestrator.nginx import regenerate_nginx_config
from orchestrator.models import OrchestratorState
from orchestrator.utils import create_docker_network


@asynccontextmanager
async def lifespan(app: FastAPI):
    conf = load_config()
    docker_client = docker.from_env()

    app.state.state = state = OrchestratorState(
        dashboard_domain=conf.get("dashboard_domain", "wikis.localhost"),
        docker_client=docker_client,
        docker_network=create_docker_network(docker_client),
        docker_nginx_container=docker_client.containers.get("mw-orchestrator-nginx"),
        kits=load_kits(conf)
    )

    state.docker_network.connect(state.docker_nginx_container)
    regenerate_nginx_config(state, reload=False)

    yield

app = FastAPI(lifespan=lifespan)

def get_state(request: Request) -> OrchestratorState:
    return request.app.state.state

@app.get("/health")
async def health():
    return {"status": "ok"}


app.mount("/", StaticFiles(directory="orchestrator/static"), name="static")
