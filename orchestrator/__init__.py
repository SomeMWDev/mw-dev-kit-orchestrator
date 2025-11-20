from fastapi import FastAPI, Response, status
from starlette.staticfiles import StaticFiles

from orchestrator.config import load_config
from orchestrator.nginx import regenerate_nginx_config
from orchestrator.utils import initialize_networks

app = FastAPI()
config = load_config()

# TODO this should be async and not prevent the bootstrapping process
initialized_networks = False
regenerate_nginx_config(config)
initialize_networks(config)
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

app.mount("/", StaticFiles(directory="orchestrator/static"), name="static")
