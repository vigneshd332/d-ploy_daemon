"""
Models for Generic Exceptions
"""

from pydantic import BaseModel


class GenericError(BaseModel):
    """Model for generic error with detail"""
    detail: str
