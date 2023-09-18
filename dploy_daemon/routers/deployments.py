"""
Router for Deployment routes
"""

import shlex
import subprocess
from fastapi import APIRouter, HTTPException, status
from dploy_daemon.config import settings
from dploy_daemon.models.deployments import CreateWithGitHTTPS

from dploy_daemon.models.exceptions import GenericError, SuccessResponse

router = APIRouter(
    prefix="/deployments",
    tags=["deployments"],
)


@router.post("/create-with-git-https", responses={200: {"model": SuccessResponse}, 500: {"model": GenericError}})
async def create_with_git(
    request: CreateWithGitHTTPS,
) -> SuccessResponse:
    """
    Create a deployment from a git repo
    """
    remote_url = "".join(["://".join([request.repo_url.split("://")[
                         0], f"{request.username}:{request.password}@"]), request.repo_url.split("://")[1]])
    try:
        process = subprocess.Popen(f"""git clone {shlex.quote(remote_url)} {shlex.quote(str(settings.deploy_dir.joinpath(request.deployment_name)))} --branch {shlex.quote(request.repo_branch)}""",
                                   shell=True,
                                   stdout=subprocess.DEVNULL,
                                   stderr=subprocess.PIPE)
        _, stderr = process.communicate()
        if process.returncode != 0:
            raise OSError(stderr.decode("utf-8"))

    except OSError as exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating deployment - {exception.strerror}",
        )
    return SuccessResponse(message=f"Deployment '{request.deployment_name}' created successfully")
