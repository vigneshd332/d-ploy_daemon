"""
Models for Deployments
"""

from typing import Optional
from pydantic import BaseModel, Field


class CreateWithGitHTTPS(BaseModel):
    deployment_name: str = Field(..., description="Name of the deployment")
    username: str = Field(..., description="Git Username")
    password: str = Field(..., description="Git Password")
    repo_url: str = Field(..., description="Git Repo URL")
    repo_branch: Optional[str] = Field("master", description="Git Repo Branch")
