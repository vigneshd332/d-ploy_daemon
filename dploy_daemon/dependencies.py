"""
Miscellaneous dependencies for the API.
"""

import subprocess
import shlex
import sys
import json

import docker
from docker.client import DockerClient
from fastapi import HTTPException, Request, status

from dploy_daemon.config import settings


async def check_authentication(request: Request) -> None:
    """
    Checks ID and secret for authentication
    """
    if (settings.environment == "dev") or (request.url == request.url_for("register")):
        return
    if str(request.headers.get("X-Dploy-Daemon-ID")) != str(settings.daemon_id):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid ID",
        )
    if str(request.headers.get("X-Dploy-Daemon-Secret")) != str(settings.daemon_secret):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid secret",
        )


async def get_docker() -> DockerClient:
    """
    Get docker client instance
    """
    return docker.from_env()

def check_sudo():
	# Checking if sudo password is correct
	process = subprocess.Popen(f"""echo {shlex.quote(str(settings.sudo_passwd))} | sudo -p '' -S -v""",
								shell=True,
								stdout=subprocess.PIPE,
								stderr=subprocess.PIPE)
	_, stderr = process.communicate()
	if stderr:
		print("Invalid sudo password")
		sys.exit(1)

def docker_init_config():
	# Checking if daemon.json exists
	process = subprocess.Popen(f"""echo {shlex.quote(str(settings.sudo_passwd))} | sudo -p '' -S ls /etc/docker/daemon.json""",
								shell=True,
								stdout=subprocess.PIPE,
								stderr=subprocess.PIPE)
	_, stderr = process.communicate()

	daemon_config = {}
	if "No such file or directory" not in stderr.decode('utf-8'):
		with open("/etc/docker/daemon.json", "r") as f:
			daemon_config = json.load(f)
	
	with open("daemon.json", "w") as f:
		daemon_config["live-restore"] = True
		json.dump(daemon_config, f, indent=4)
	
	process = subprocess.Popen(f"""echo {shlex.quote(str(settings.sudo_passwd))} | sudo -p '' -S cp daemon.json /etc/docker/daemon.json && \
								sudo -p '' -S rm daemon.json && \
								sudo -p '' -S systemctl daemon-reload""",
								shell=True,
								stdout=subprocess.PIPE,
								stderr=subprocess.PIPE)
	_, stderr = process.communicate()
	if stderr:
		print("Error executing docker config script")
		sys.exit(1)

def firewall_init_config():
	# Creating dploy_zone if it doesn't exist
	if settings.dploy_zone not in str(subprocess.check_output(f"echo {shlex.quote(str(settings.sudo_passwd))} | sudo -p '' -S firewall-cmd --get-zones", shell=True)):
		process = subprocess.Popen(f"""echo {shlex.quote(str(settings.sudo_passwd))} | sudo -p '' -S firewall-cmd \
									--permanent \
									--new-zone={shlex.quote(settings.dploy_zone)} && \
									echo {shlex.quote(str(settings.sudo_passwd))} | sudo -p '' -S firewall-cmd --complete-reload""",
									shell=True,
									stdout=subprocess.PIPE,
									stderr=subprocess.PIPE)

		_, stderr = process.communicate()
		if stderr:
			print("Error creating firewall deployment zone")
			sys.exit(1)
		

	# Create blacklist zone if it doesn't exist
	if settings.dploy_blacklist_zone not in str(subprocess.check_output(f"echo {shlex.quote(str(settings.sudo_passwd))} | sudo -p '' -S firewall-cmd --get-zones", shell=True)):
		process = subprocess.Popen(f"""echo {shlex.quote(str(settings.sudo_passwd))} | sudo -p '' -S firewall-cmd \
									--permanent \
									--new-zone={shlex.quote(settings.dploy_blacklist_zone)} && \
									echo {shlex.quote(str(settings.sudo_passwd))} | sudo -p '' -S firewall-cmd --complete-reload""",
									shell=True,
									stdout=subprocess.PIPE,
									stderr=subprocess.PIPE)

		_, stderr = process.communicate()
		if stderr:
			print("Error creating blacklist zone")
			sys.exit(1)
	
	# Execute firewall script for docker
	# process = subprocess.Popen(f"echo {shlex.quote(str(settings.sudo_passwd))} | sudo -p '' -S scripts/firewall.sh",
	# 							shell=True,
	# 							stdout=subprocess.PIPE,
	# 							stderr=subprocess.PIPE)
	# _, stderr = process.communicate()
	# if stderr and "ALREADY_ENABLED" not in stderr.decode('utf-8') and "NOT_ENABLED" not in stderr.decode('utf-8'):
	# 	print("Error executing firewall script for docker setup")
	# 	sys.exit(1)
	
#Restart docker
def restart_docker():
	process = subprocess.Popen(f"echo {shlex.quote(str(settings.sudo_passwd))} | sudo -p '' -S systemctl restart docker",
								shell=True,
								stdout=subprocess.PIPE,
								stderr=subprocess.PIPE)
	_, stderr = process.communicate()
	if stderr:
		print("Error restarting docker")
		sys.exit(1)

# Restart firewalld
def restart_firewalld():
	process = subprocess.Popen(f"echo {shlex.quote(str(settings.sudo_passwd))} | sudo -p '' -S systemctl restart firewalld",
								shell=True,
								stdout=subprocess.PIPE,
								stderr=subprocess.PIPE)
	_, stderr = process.communicate()
	if stderr:
		print("Error restarting firewalld")
		sys.exit(1)
