import asyncio
from contextlib import asynccontextmanager

import docker
import docker.errors
from fastapi import FastAPI, Depends
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.staticfiles import StaticFiles

from orchestrator.config import load_config, load_kits
from orchestrator.events import handle_docker_events
from orchestrator.models import OrchestratorState
from orchestrator.nginx import regenerate_nginx_config
from orchestrator.utils import create_docker_network

conf = load_config()
dashboard_domain = conf.get("dashboard_domain", "wikis.localhost")

@asynccontextmanager
async def lifespan(app: FastAPI):
    docker_client = docker.from_env()

    app.state.state = state = OrchestratorState(
        dashboard_domain=dashboard_domain,
        docker_client=docker_client,
        docker_network=create_docker_network(docker_client),
        docker_nginx_container=docker_client.containers.get("mw-orchestrator-nginx"),
        kits=load_kits(conf, docker_client)
    )

    try:
        state.docker_network.connect(state.docker_nginx_container)
    except docker.errors.APIError:
        # nginx is already connected - this should only happen when using hot reload
        print("Failed to connect nginx container to network")
    regenerate_nginx_config(state, reload=False)
    asyncio.create_task(event_loop(state))
    yield

app = FastAPI(lifespan=lifespan)

# TODO: remove this! the API should be on the same host as the dashboard
origins = ["http://localhost:5173", dashboard_domain]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_state(request: Request) -> OrchestratorState:
    return request.app.state.state

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/kits")
async def kits(
        state: OrchestratorState = Depends(get_state)
):
    return state.kits

app.mount("/", StaticFiles(directory="orchestrator/static"), name="static")

async def event_loop(state: OrchestratorState):
    print("Handling events...")
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, handle_docker_events, state)
