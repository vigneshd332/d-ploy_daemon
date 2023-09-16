"""
Miscellaneous dependencies for the API.
"""

import docker
from docker.client import DockerClient
from fastapi import HTTPException, Request, status

from dploy_daemon.config import settings


async def check_authentication(request: Request) -> None:
    """
    Checks ID and secret for authentication
    """
    if (settings.environment == "dev"):
        return

    if str(request.headers.get("X-Dploy-Daemon-ID")) != str(settings.daemon_id):
        print(str(settings.daemon_id), request.headers.get("X-Dploy-Daemon-ID"))
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
