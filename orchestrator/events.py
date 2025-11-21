import datetime

from docker.types import CancellableStream

from orchestrator.models import OrchestratorState, KitStatus
from orchestrator.nginx import regenerate_nginx_config


def handle_docker_events(state: OrchestratorState):
    events: CancellableStream = state.docker_client.events(
        since=datetime.datetime.now(datetime.UTC),
        decode=True,
    )

    state_changed = False
    for event in events:
        event_type = event.get("Type")
        if event_type != "container":
            continue
        actor = event.get("Actor")
        if actor is None:
            continue
        attributes = actor.get("Attributes")
        if attributes is None:
            continue
        name = attributes.get("name")
        if name is None:
            continue

        associated_kit = None
        for kit in state.kits.values():
            if kit.web_container == name:
                associated_kit = kit
                break
        if associated_kit is None:
            if not name.startswith("mw-orchestrator"):
                print(f"Couldn't find a kit for {name}")
            continue
        action = event.get("Action")
        if action == "stop":
            associated_kit.status = KitStatus.EXITED
            state_changed = True
            print(f"{name} stopped")
        elif action == "start":
            associated_kit.status = KitStatus.RUNNING
            state_changed = True
            print(f"{name} started")

    if state_changed:
        regenerate_nginx_config(state, reload=True)
