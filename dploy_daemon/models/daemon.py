"""
Models for Daemon
"""

from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    """Register Request"""
    id: str = Field(..., description="Daemon ID")
    auth_key: str = Field(..., description="Daemon Secret")
