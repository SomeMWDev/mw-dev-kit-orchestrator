from pathlib import Path

import docker.errors

from orchestrator.models import MWDevKit, OrchestratorState, KitStatus


def build_nginx_config(state: OrchestratorState) -> str:
    conf = """
server {
    listen 80 default_server;
    server_name _;

    return 404;
}"""
    if state.dashboard_domain != "":
        conf += f"""
server {{
    listen 80;
    server_name {state.dashboard_domain};
    
    #location / {{
    #    proxy_pass http://mw-orchestrator-dash:5173;
    #    proxy_set_header Host $host;
    #    proxy_set_header X-Real-IP $remote_addr;
    #}}
    
    location /api/ {{
        proxy_pass http://mw-orchestrator:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }}
}}
        """

    return conf

def build_upstream(kit: MWDevKit, connect: bool) -> str:
    # use real server if container is online, otherwise redirect to port 9 to discard
    upstream = f"server {kit.web_container}:8080;" if connect else "server 127.0.0.1:9;"
    upstream_name = f"mediawiki-{kit.name}"
    return f"""
upstream {upstream_name} {{
    {upstream}
}}

server {{
    listen {kit.port};
    server_name {kit.domain};

    location / {{
        proxy_pass http://{upstream_name};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }}
}}"""

def build_upstreams(state: OrchestratorState) -> dict[str, str]:
    upstreams = {}
    for kit in state.kits.values():
        is_online = kit.connect_initially or (kit.status in [KitStatus.RUNNING.value, KitStatus.HEALTHY.value])
        upstreams[kit.name] = build_upstream(kit, is_online)
        if is_online:
            container = state.docker_client.containers.get(kit.web_container)
            # connect container to the orchestrator network
            try:
                state.docker_network.connect(container)
            except docker.errors.APIError:
                print(f"Failed to connect {kit.web_container} - is it already in the network?")

    return upstreams


def regenerate_nginx_config(state: OrchestratorState, reload: bool):
    conf_folder = Path("nginx/conf.d")
    for file in conf_folder.iterdir():
        if file.is_file():
            file.unlink()

    with open(conf_folder / "base.conf", "w") as file:
        file.write(build_nginx_config(state))

    upstreams = build_upstreams(state)
    for upstream_name, upstream in upstreams.items():
        with open(conf_folder / f"{upstream_name}.conf", "w") as file:
            file.write(upstream)

    if reload:
        state.docker_nginx_container.exec_run(["nginx", "-s", "reload"])
