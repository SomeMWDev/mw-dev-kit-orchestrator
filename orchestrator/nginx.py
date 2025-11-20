from orchestrator.config import get_kits


def build_nginx_config(config) -> str:
    # TODO allow disabling if value is empty
    dashboard_domain = config.get("dashboard_domain", "wikis.localhost")
    nginx_config = f"""
server {{
    listen 80 default_server;
    server_name _;

    return 404;
}}

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

    for kit, data in get_kits(config):
        domain = data.get("domain")
        port = data.get("port", 80)
        internal_host = data.get("internal-host", f"{kit}-mediawiki-web-1")
        nginx_config += f"""
server {{
    listen {port};
    server_name {domain};

    location / {{
        proxy_pass http://{internal_host}:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }}
}}
        """

    return nginx_config

def regenerate_nginx_config(config):
    with open("nginx/nginx.conf", "w") as file:
        file.write(build_nginx_config(config))

def get_networks(config) -> list[str]:
    networks = []

    for kit, data in get_kits(config):
        networks.append(data.get("network", f"{kit}_mw"))

    return networks
