"""
Models for Docker API
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class SuccessResponse(BaseModel):
    """Model for success response"""
    message: str = Field(..., description="Info message")


class CreateContainerRequest(BaseModel):
    """Model for create container request"""
    image: str = Field(..., description="Image name")
    name: str = Field(..., description="Container name")
    ports: Optional[dict[str, int]] = Field(
        None, description="Container ports")


class ContainerDetails(BaseModel):
    """Details of a Single Docker Container"""
    id: str = Field(..., description="Container ID")
    name: str = Field(..., description="Container Name")
    status: str = Field(..., description="Container Status")
    image: List[str] = Field(None, description="Image Name")
    ports: dict[str, List[dict[str, str]]] = Field(
        None, description="Container Ports")
    created: str = Field(..., description="Container Creation Time")


class DeleteRequest(BaseModel):
    """Model for delete request"""
    container_id: str = Field(..., description="Container ID")
    force: bool = Field(False, description="Force delete")
    v: bool = Field(False, description="Remove volumes")
