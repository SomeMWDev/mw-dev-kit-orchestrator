from contextlib import asynccontextmanager

import docker
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from orchestrator.config import load_config
from orchestrator.nginx import regenerate_nginx_config
from orchestrator.utils import initialize_networks


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.config = load_config()
    app.docker_client = docker.from_env()
    regenerate_nginx_config(app.config, app.docker_client)
    initialize_networks(app.config, app.docker_client)
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/health")
async def health():
    return {"status": "ok"}


app.mount("/", StaticFiles(directory="orchestrator/static"), name="static")
