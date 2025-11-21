from docker.types import CancellableStream

from orchestrator.models import OrchestratorState, KitStatus


def handle_docker_events(state: OrchestratorState):
    events: CancellableStream = state.docker_client.events(
        since=state.last_polling_timestamp,
        decode=True,
    )

    for event in events:
        event_type = event["Type"]
        if event_type != "container":
            continue
        name = event["Actor"]["Attributes"]["name"]
        associated_kit = None
        for kit in state.kits.values():
            if kit.web_container == name:
                associated_kit = kit
                break
        if associated_kit is None:
            if not name.startswith("mw-orchestrator"):
                print(f"Couldn't find a kit for {name}")
            continue
        action = event["Action"]
        if action == "stop":
            associated_kit.status = KitStatus.EXITED
            print(f"{name} stopped")
        elif action == "start":
            associated_kit.status = KitStatus.RUNNING
            print(f"{name} started")

    state.update_polling_timestamp()
