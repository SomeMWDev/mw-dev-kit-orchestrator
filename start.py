# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "pyyaml",
# ]
# ///
import subprocess

import yaml

with open("config.yml", "r") as file:
    config = yaml.safe_load(file)

nginx_config = """
server {
    listen 80 default_server;
    server_name _;

    return 404;
}
"""

networks = []
for kit, data in config["kits"].items():
    network = data.get("network", f"{kit}_mw")
    networks.append(network)
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

with open("nginx/nginx.conf", "w") as file:
    file.write(nginx_config)

command = [
    "docker",
    "run",
    # "-d",
    "--name",
    "mw-orchestrator-nginx",
    "-p",
    "80:80",
    "-v",
    "./nginx/nginx.conf:/etc/nginx/conf.d/nginx.conf:ro",
]

for network in networks:
    command += ["--network", network]

command.append("nginx:latest")

# stop and remove old container if present
subprocess.run(["docker", "stop", "mw-orchestrator-nginx"])
subprocess.run(["docker", "rm", "mw-orchestrator-nginx"])
# start new container
subprocess.run(command, check=True)
