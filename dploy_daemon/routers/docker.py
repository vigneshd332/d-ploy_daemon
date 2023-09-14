"""
Router for Docker routes
"""

import logging

from docker.client import DockerClient
from docker.errors import APIError, NotFound
from docker.models.containers import Container
from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends

from dploy_daemon.dependencies import get_docker
from dploy_daemon.models.docker import (ContainerDetails,
                                        CreateContainerRequest, DeleteRequest,
                                        )
from dploy_daemon.models.exceptions import GenericError, SuccessResponse

router = APIRouter(
    prefix="/docker",
    tags=["docker"],
)


@router.post("/containers/create",
             response_model=ContainerDetails,
             responses={
                 status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": GenericError},
             }
             )
async def create_container(create_request: CreateContainerRequest, docker_client: DockerClient = Depends(get_docker)) -> ContainerDetails:
    """
    Create container
    """
    try:
        container: Container = docker_client.containers.run(
            create_request.image,
            name=create_request.name,
            ports=create_request.ports,
            detach=True
        )
        container_response: ContainerDetails = ContainerDetails(
            id=container.id,
            status=container.status,
            image=container.image.tags,
            name=container.name,
            ports=container.ports,
            created=container.attrs['Created'])

    except APIError as api_error_exception:
        logging.exception("Error creating the container %s",
                          create_request.name)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) from api_error_exception

    return container_response


@router.get("/containers/{container_id}",
            response_model=ContainerDetails,
            responses={
                status.HTTP_404_NOT_FOUND: {"model": GenericError},
                status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": GenericError},
            }
            )
async def get_container_details(container_id: str, docker_client: DockerClient = Depends(get_docker)) -> ContainerDetails:
    """
    Get container details
    """
    try:
        container: Container = docker_client.containers.get(container_id)
        container_response: ContainerDetails = ContainerDetails(
            id=container.id,
            status=container.status,
            image=container.image.tags,
            name=container.name,
            ports=container.ports,
            created=container.attrs['Created'])

    except NotFound as not_found_exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Container not found"
        ) from not_found_exception
    except APIError as api_error_exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) from api_error_exception
    return container_response


@router.post(
    "/containers/delete",
    responses={
        status.HTTP_404_NOT_FOUND: {"model": GenericError},
        status.HTTP_403_FORBIDDEN: {"model": GenericError},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": GenericError}
    }
)
async def delete_container(
    delete_request: DeleteRequest,
    docker_client: DockerClient = Depends(get_docker)
) -> SuccessResponse:
    """
    Delete container
    """
    container = Container()
    try:
        container = docker_client.containers.get(delete_request.container_id)
        container.remove(force=delete_request.force, v=delete_request.v)
    except NotFound as not_found_exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Container not found") from not_found_exception
    except APIError as api_error_exception:
        if container.status == "running":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot remove running containers, try forcing") from api_error_exception
        logging.exception(
            "Error deleting the container %s",
            delete_request.container_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) from api_error_exception

    return SuccessResponse(message=f"Container {delete_request.container_id} deleted")


@router.post(
    "/containers/{container_id}/start",
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": GenericError}
    }
)
async def start_container(
    container_id: str,
    docker_client: DockerClient = Depends(get_docker)
) -> SuccessResponse:
    """
    Start container
    """
    try:
        container: Container = docker_client.containers.get(container_id)
        container.start()
    except NotFound as not_found_exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Container not found") from not_found_exception
    except APIError as api_error_exception:
        logging.exception("Error starting the container %s", container_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) from api_error_exception

    return SuccessResponse(message=f"Container {container_id} started")


@router.post(
    "/containers/{container_id}/stop",
    responses={
        status.HTTP_404_NOT_FOUND: {"model": GenericError},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": GenericError}
    })
async def stop_container(
    container_id: str,
    docker_client: DockerClient = Depends(get_docker)
) -> SuccessResponse:
    """
    Stop container
    """
    try:
        container: Container = docker_client.containers.get(container_id)
        container.stop()
    except NotFound as not_found_exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Container not found") from not_found_exception
    except APIError as api_error_exception:
        logging.exception("Error stopping the container %s", container_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) from api_error_exception

    return SuccessResponse(message=f"Container {container_id} stopped")


@router.post(
    "/containers/{container_id}/restart",
    responses={
        status.HTTP_404_NOT_FOUND: {"model": GenericError},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": GenericError}
    })
async def restart_container(
    container_id: str,
    docker_client: DockerClient = Depends(get_docker)
) -> SuccessResponse:
    """
    Restart container
    """
    try:
        container: Container = docker_client.containers.get(container_id)
        container.restart()
    except NotFound as not_found_exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Container not found") from not_found_exception
    except APIError as api_error_exception:
        logging.exception("Error restarting the container %s", container_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) from api_error_exception

    return SuccessResponse(message=f"Container {container_id} restarted")


@router.post(
    "/containers/{container_id}/kill",
    responses={
        status.HTTP_404_NOT_FOUND: {"model": GenericError},
        status.HTTP_403_FORBIDDEN: {"model": GenericError},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": GenericError}
    })
async def kill_container(
    container_id: str,
    docker_client: DockerClient = Depends(get_docker)
) -> SuccessResponse:
    """
    Kill container
    """
    container = Container()
    try:
        container = docker_client.containers.get(container_id)
        container.kill()
    except NotFound as not_found_exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Container not found") from not_found_exception
    except APIError as api_error_exception:
        if container.status != "running":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot kill containers that are not running") from api_error_exception
        logging.exception("Error killing the container %s", container_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) from api_error_exception

    return SuccessResponse(message=f"Container {container_id} killed")
