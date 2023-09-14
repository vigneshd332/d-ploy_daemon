"""
Models for Generic Exceptions
"""

from pydantic import BaseModel, Field


class SuccessResponse(BaseModel):
    """Model for success response"""
    message: str = Field(..., description="Info message")


class GenericError(BaseModel):
    """Model for generic error with detail"""
    detail: str
