from pathlib import Path

from docker import DockerClient
from docker.models.containers import Container
from docker.models.networks import Network

from orchestrator.config import get_kits


def build_nginx_config(config) -> str:
    dashboard_domain = config.get("dashboard_domain", "wikis.localhost")
    conf = """
server {
    listen 80 default_server;
    server_name _;

    return 404;
}"""
    if dashboard_domain != "":
        conf += f"""
server {{
    listen 80;
    server_name {dashboard_domain};
    
    location / {{
        proxy_pass http://mw-orchestrator:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }}
}}
        """

    return conf

def build_upstream(kit_name, data, connect) -> str:
    domain = data.get("domain")
    port = data.get("port", 80)
    # TODO don't recompute this, instead use generated kits array instead of config
    internal_host = data.get("internal-host", f"{kit_name}-mediawiki-web-1")
    # use real server if container is online, otherwise redirect to port 9 to discard
    upstream = f"server {internal_host}:8080;" if connect else "server 127.0.0.1:9;"
    upstream_name = f"mediawiki-{kit_name}"
    return f"""
upstream {upstream_name} {{
    {upstream}
}}

server {{
    listen {port};
    server_name {domain};

    location / {{
        proxy_pass http://{upstream_name};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }}
}}"""

def build_upstreams(config, docker_client: DockerClient, docker_network: Network) -> dict[str, str]:
    upstreams = {}
    for kit_name, data in get_kits(config):
        is_online = data.get("connect-initially", False)
        # TODO don't recompute this - also the host doesn't have to be the container name
        internal_host = data.get("internal-host", f"{kit_name}-mediawiki-web-1")
        container = None
        try:
            container = docker_client.containers.get(internal_host)
        except Exception as e:
            is_online = False
            print(f"{internal_host} is not online: {e}")
        if container and not is_online:
            is_online = container.status in ["running", "healthy"]
            print(f"Container {internal_host} is {container.status}")
        upstreams[kit_name] = build_upstream(kit_name, data, is_online)
        if is_online:
            # connect container to the orchestrator network
            try:
                docker_network.connect(container)
            except:
                print(f"Failed to connect {internal_host} - is it already in the network?")

    return upstreams


def regenerate_nginx_config(config, docker_client: DockerClient, docker_network: Network, nginx_container: Container,
                            reload: bool):
    conf_folder = Path("nginx/conf.d")
    for file in conf_folder.iterdir():
        if file.is_file():
            file.unlink()

    with open(conf_folder / "base.conf", "w") as file:
        file.write(build_nginx_config(config))

    upstreams = build_upstreams(config, docker_client, docker_network)
    for upstream_name, upstream in upstreams.items():
        with open(conf_folder / f"{upstream_name}.conf", "w") as file:
            file.write(upstream)

    if reload:
        nginx_container.exec_run(["nginx", "-s", "reload"])


def get_networks(config) -> list[str]:
    networks = []

    for kit, data in get_kits(config):
        networks.append(data.get("network", f"{kit}_mw"))

    return networks
