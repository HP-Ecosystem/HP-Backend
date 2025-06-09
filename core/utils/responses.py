from typing import Any

from rest_framework import status
from rest_framework.response import Response


class StandardResponse:
    """
    Utility class for creating consistent API responses.

    Provides static methods for common HTTP response patterns:
        - success (200)
        - created (201)
        - updated (202)
        - deleted (204)
    """

    @staticmethod
    def success(
        data: Any = None,
        message: str = "success",
        status_code: int = status.HTTP_200_OK,
    ) -> Response:
        """
        Return a standard success response.

        Args:
            data: Optional response data.
            message: Optional message string.
            status_code: HTTP status code (default 200).

        Returns:
            Response: DRF Response object.
        """
        return Response(
            {"success": True, "message": message, "data": data}, status=status_code
        )

    @staticmethod
    def created(
        data: Any = None, message: str = "Resource created successfully"
    ) -> Response:
        """
        Return a 201 created response.

        Args:
            data: Optional response data.
            message: Optional message string.

        Returns:
            Response: DRF Response object with 201 status.
        """
        return StandardResponse.success(
            data=data, message=message, status_code=status.HTTP_201_CREATED
        )

    @staticmethod
    def updated(
        data: Any = None, message: str = "Resource updated successfully"
    ) -> Response:
        """
        Return a 202 updated response.

        Args:
            data: Optional response data.
            message: Optional message string.

        Returns:
            Response: DRF Response object with 202 status.
        """
        return StandardResponse.success(
            data=data, message=message, status_code=status.HTTP_202_ACCEPTED
        )

    @staticmethod
    def deleted(message: str = "Resource deleted successfully") -> Response:
        """
        Return a 204 no content response.

        Args:
            message: Optional message string.

        Returns:
            Response: DRF Response object with 204 status.
        """
        return Response(
            {"success": True, "message": message}, status=status.HTTP_204_NO_CONTENT
        )
