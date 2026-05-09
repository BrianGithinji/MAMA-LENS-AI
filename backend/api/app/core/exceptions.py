"""
MAMA-LENS AI — Custom Exception Classes
"""

from fastapi import status


class MamaLensException(Exception):
    """Base exception for MAMA-LENS AI."""

    def __init__(
        self,
        message: str,
        error_code: str = "MAMALENS_ERROR",
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: dict = None,
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


class AuthenticationError(MamaLensException):
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class AuthorizationError(MamaLensException):
    def __init__(self, message: str = "You do not have permission to perform this action"):
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            status_code=status.HTTP_403_FORBIDDEN,
        )


class NotFoundError(MamaLensException):
    def __init__(self, resource: str = "Resource"):
        super().__init__(
            message=f"{resource} not found",
            error_code="NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class ValidationError(MamaLensException):
    def __init__(self, message: str, details: dict = None):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details,
        )


class ConflictError(MamaLensException):
    def __init__(self, message: str):
        super().__init__(
            message=message,
            error_code="CONFLICT",
            status_code=status.HTTP_409_CONFLICT,
        )


class RateLimitError(MamaLensException):
    def __init__(self):
        super().__init__(
            message="Too many requests. Please slow down.",
            error_code="RATE_LIMIT_EXCEEDED",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        )


class ExternalServiceError(MamaLensException):
    def __init__(self, service: str, message: str = None):
        super().__init__(
            message=message or f"External service '{service}' is unavailable",
            error_code="EXTERNAL_SERVICE_ERROR",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


class EmergencyDetectedError(MamaLensException):
    """Raised when an emergency health situation is detected."""

    def __init__(self, message: str, emergency_type: str, recommended_action: str):
        super().__init__(
            message=message,
            error_code="EMERGENCY_DETECTED",
            status_code=status.HTTP_200_OK,
            details={
                "emergency_type": emergency_type,
                "recommended_action": recommended_action,
                "call_emergency": True,
            },
        )
