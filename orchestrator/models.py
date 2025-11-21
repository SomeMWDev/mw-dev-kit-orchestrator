from dataclasses import dataclass
from datetime import datetime, UTC
from enum import Enum

from docker import DockerClient
from docker.models.containers import Container
from docker.models.networks import Network

class KitStatus(Enum):
    UNKNOWN = "unknown"

    CREATED = "created"
    RUNNING = "running"
    HEALTHY = "healthy"
    RESTARTING = "restarting"
    EXITED = "exited"
    PAUSED = "paused"
    DEAD = "dead"

@dataclass
class MWDevKit:
    name: str
    domain: str
    port: int
    web_container: str
    # TODO can we remove this?
    connect_initially: bool
    status: KitStatus


@dataclass
class OrchestratorState:
    dashboard_domain: str
    docker_client: DockerClient
    docker_network: Network
    docker_nginx_container: Container
    kits: dict[str, MWDevKit]
    last_polling_timestamp: datetime

    def update_polling_timestamp(self):
        self.last_polling_timestamp = datetime.now(UTC)
