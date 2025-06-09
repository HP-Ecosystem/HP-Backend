from typing import Any

from rest_framework import status
from rest_framework.exceptions import APIException


class BaseAPIException(APIException):
    """
    Base exception class for all custom API exceptions.

    Provides a consistent structure for custom API errors.
    """

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "An error occurred"
    default_code = "error"

    def __init__(
        self, detail: str | dict[str, Any] | None = None, code: str | None = None
    ):
        """
        Initialize the exception.

        Args:
            detail: Optional error detail message or dictionary.
            code: Optional error code string.
        """
        if detail is None:
            detail = self.default_detail
        if code is None:
            code = self.default_code
        super().__init__(detail=detail, code=code)


class ConflictError(BaseAPIException):
    """
    Exception for conflict errors (409).

    Used when a request conflicts with the current state of the resource.
    """

    status_code = status.HTTP_409_CONFLICT
    default_detail = "Request conflicts with current state."
    default_code = "conflict"


class UnprocessableEntityError(BaseAPIException):
    """
    Exception for unprocessable entity errors (422).

    Used when the server understands the request but cannot process it.
    """

    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = "Unable to process the request."
    default_code = "unprocessable_entity"


class BadRequestError(BaseAPIException):
    """
    Exception for bad request errors (400).

    Used when the request is malformed or invalid.
    """

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Bad request."
    default_code = "bad_request"
