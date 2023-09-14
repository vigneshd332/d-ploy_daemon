"""
Miscellaneous dependencies for the API.
"""

import docker
from docker.client import DockerClient


async def check_authentication() -> None:
    """
    TODO: To be implemented
    """
    pass  # pylint: disable=unnecessary-pass


async def get_docker() -> DockerClient:
    """
    Get docker client instance
    """
    return docker.from_env()
