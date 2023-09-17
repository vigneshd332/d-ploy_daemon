"""
Models for the Docker Compose API
"""

from typing import Optional
from pydantic import BaseModel, Field


class UpRequest(BaseModel):
    """
    Request model for docker compose up
    """
    compose_file: str = Field(
        ..., description="Path to docker-compose.yml file relative to the project root")
    deployment_name: str = Field(..., description="Name of the deployment")
    service: Optional[str] = Field(
        description="Names of the services to start seperated by space")
    build: Optional[bool] = Field(
        False, description="Re-Build images before starting containers")
    no_cache: Optional[bool] = Field(
        False, description="Do not use cache when building the image")


class DownRequest(BaseModel):
    """
    Request model for docker compose down
    """
    compose_file: str = Field(
        ..., description="Path to docker-compose.yml file relative to the project root")
    deployment_name: str = Field(..., description="Name of the deployment")
    service: Optional[str] = Field(
        description="Name of the service to stop")
