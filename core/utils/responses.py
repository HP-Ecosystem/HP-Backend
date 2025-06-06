from typing import Any

from rest_framework import status
from rest_framework.response import Response


class StandardResponse:
    """Utility class for creating consistent API responses."""

    @staticmethod
    def success(
        data: Any = None,
        message: str = "success",
        status_code: int = status.HTTP_200_OK,
    ) -> Response:
        """Create a success response."""

        return Response(
            {"success": True, "message": message, "data": data}, status=status_code
        )

    @staticmethod
    def created(
        data: Any = None, message: str = "Resource created successfully"
    ) -> Response:
        """Create a 201 created response."""

        return StandardResponse.success(
            data=data, message=message, status_code=status.HTTP_201_CREATED
        )

    @staticmethod
    def updated(
        data: Any = None, message: str = "Resource updated successfully"
    ) -> Response:
        """Create a 202 updated response."""

        return StandardResponse.success(
            data=data, message=message, status_code=status.HTTP_202_ACCEPTED
        )

    @staticmethod
    def deleted(message: str = "Resource deleted successfully") -> Response:
        """Create a 204 no content response."""

        return Response(
            {"success": True, "message": message}, status=status.HTTP_204_NO_CONTENT
        )
