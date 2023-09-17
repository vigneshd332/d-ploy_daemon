"""
Router for Docker Compose commands
"""

import subprocess
import shlex

from fastapi import APIRouter, HTTPException, status
from dploy_daemon.config import settings
from dploy_daemon.models.docker_compose import DownRequest, UpRequest

from dploy_daemon.models.exceptions import GenericError, SuccessResponse

router = APIRouter(
    prefix="/docker-compose",
    tags=["docker-compose"],
)


@router.post("/up",
             responses={
                 status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": GenericError},
                 status.HTTP_200_OK: {"model": SuccessResponse},
             })
async def up(
    up_request: UpRequest,
) -> SuccessResponse:
    """
    Execute a docker compose up request
    """
    deploy_path = settings.deploy_dir.joinpath(
        up_request.deployment_name, up_request.compose_file)
    if not deploy_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deployment not found",
        )
    try:
        subprocess.Popen(f"""docker compose -f {shlex.quote(str(deploy_path))} up -d
                         {shlex.quote(up_request.service) if up_request.service else ''}
                         {'--build' if up_request.build else ''}
                         {'--no-cache' if up_request.no_cache else ''} &""",
                         shell=True,
                         stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL)
    except OSError as exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error starting deployment - {exception.strerror}",
        )
    return SuccessResponse(message="Deployment started successfully")


@router.post("/down",
             responses={
                 status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": GenericError},
                 status.HTTP_200_OK: {"model": SuccessResponse},
             })
async def down(
    down_request: DownRequest,
) -> SuccessResponse:
    """
    Execute a docker compose down request
    """
    deploy_path = settings.deploy_dir.joinpath(
        down_request.deployment_name, down_request.compose_file)
    if not deploy_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deployment not found",
        )
    try:
        subprocess.Popen(f"""docker compose -f {shlex.quote(str(deploy_path))} down
                         {shlex.quote(down_request.service if down_request.service else '')} &""",
                         shell=True,
                         stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL)
    except OSError as exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error stopping deployment - {exception.strerror}",
        )
    return SuccessResponse(message="Deployment stopped successfully")
