"""
Miscellaneous dependencies for the API.
"""

import subprocess
import shlex
import sys

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


def firewall_init_config():
    # Checking if sudo password is correct
    process = subprocess.Popen(f"""echo {shlex.quote(str(settings.sudo_passwd))} | sudo -p '' -S -v""",
                               shell=True,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if stderr:
        print("Invalid sudo password")
        sys.exit(1)

    # Creating dploy_zone if it doesn't exist
    if settings.dploy_zone not in str(subprocess.check_output(f"echo {shlex.quote(str(settings.sudo_passwd))} | sudo -p '' -S firewall-cmd --get-zones", shell=True)):
        process = subprocess.Popen(f"""echo {shlex.quote(str(settings.sudo_passwd))} | sudo -p '' -S firewall-cmd \
									--permanent \
									--new-zone={shlex.quote(settings.dploy_zone)} && \
									echo {shlex.quote(str(settings.sudo_passwd))} | sudo -p '' -S firewall-cmd --reload""",
                                   shell=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)

        stdout, stderr = process.communicate()
        if stderr:
            print("Error creating firewall deployment zone")
            sys.exit(1)

        # Add IP 0.0.0.0/0 to dploy_zone to accept all traffic by default
        process = subprocess.Popen(f"""echo {shlex.quote(str(settings.sudo_passwd))} | sudo -p '' -S firewall-cmd \
									--permanent \
									--zone={shlex.quote(settings.dploy_zone)} \
									--add-source=0.0.0.0/0 && \
									echo {shlex.quote(str(settings.sudo_passwd))} | sudo -p '' -S firewall-cmd --reload""",
                                   shell=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if stderr:
            print("Error adding source 0.0.0.0/0 to dploy_zone")
            sys.exit(1)

    # Change default zone to drop
    if "drop" not in str(subprocess.check_output(f"echo {shlex.quote(str(settings.sudo_passwd))} | sudo -p '' -S firewall-cmd --get-default-zone", shell=True)):
        process = subprocess.Popen(f"""echo {shlex.quote(str(settings.sudo_passwd))} | sudo -p '' -S firewall-cmd \
									--set-default-zone=drop && \
									echo {shlex.quote(str(settings.sudo_passwd))} | sudo -p '' -S firewall-cmd --reload""",
                                   shell=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if stderr:
            print("Error changing default zone")
            sys.exit(1)

    # Create blacklist zone if it doesn't exist
    if settings.dploy_blacklist_zone not in str(subprocess.check_output(f"echo {shlex.quote(str(settings.sudo_passwd))} | sudo -p '' -S firewall-cmd --get-zones", shell=True)):
        process = subprocess.Popen(f"""echo {shlex.quote(str(settings.sudo_passwd))} | sudo -p '' -S firewall-cmd \
									--permanent \
									--new-zone={shlex.quote(settings.dploy_blacklist_zone)} && \
									echo {shlex.quote(str(settings.sudo_passwd))} | sudo -p '' -S firewall-cmd --reload""",
                                   shell=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)

        stdout, stderr = process.communicate()
        if stderr:
            print("Error creating blacklist zone")
            sys.exit(1)
