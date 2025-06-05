"""Core exceptions module."""

from .base import (
    BadRequestError,
    BaseAPIException,
    ConflictError,
    UnprocessableEntityError,
)
from .handler import hp_exception_handler

__all__ = [
    "BaseAPIException",
    "ConflictError",
    "UnprocessableEntityError",
    "BadRequestError",
    "hp_exception_handler",
]
