from datetime import datetime, timezone
from enum import Enum
from fastapi import HTTPException, status
from typing import Optional, Dict, Any


from app.logging import logger

class ErrorLevel(Enum):
    """Error severity levels for logging"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class APIError(HTTPException):    
    def __init__(
        self,
        status_code: int,
        detail: Optional[str]=None,
        user_message: Optional[str] = None,
        log_level: ErrorLevel = ErrorLevel.ERROR,
        log_message: Optional[str] = None,
        headers: Optional[Dict[str, Any]] = None,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Args:
            status_code: HTTP status code
            detail: Technical error detail for developers
            user_message: User-friendly message for end users
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_message: Custom log message (defaults to detail if not provided)
            headers: Optional HTTP headers
            error_code: Custom error code for tracking
            context: Additional context data for logging
        """
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        
        self.user_message = user_message or detail
        self.log_level = log_level
        self.error_code = error_code
        self.context = context or {}
        
        self._log_error(log_message or detail)
    
    def _log_error(self, message: str):
        log_context = {
            "status_code": self.status_code,
            "error_code": self.error_code,
            "user_message": self.user_message,
            **self.context
        }
        
        log_method = getattr(logger, self.log_level.value)
        log_method(f"{message} | Context: {log_context}")
    
    def to_dict(self) -> Dict[str, Any]:
        return {    
            "error": True,
            "status_code": self.status_code,
            "message": self.user_message,
            "error_code": self.error_code,
            "timestamp": self._get_timestamp()
        }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for error tracking"""
        return datetime.now(timezone.utc).isoformat() + "Z"


class ErrorFactory:
    
    @staticmethod
    def not_found(
        resource: str = "Resource",
        user_message: Optional[str] = None,
        error_code: str = "RESOURCE_NOT_FOUND",
        context: Optional[Dict[str, Any]] = None
    ) -> APIError:
        """Create a 404 Not Found error"""
        user_msg = user_message or f"The requested {resource.lower()} could not be found"
        
        return APIError(
            status_code=status.HTTP_404_NOT_FOUND,
            user_message=user_msg,
            log_level=ErrorLevel.WARNING,
            error_code=error_code,
            context=context or {"resource": resource}
        )
    
    @staticmethod
    def validation_error(
        field: str,
        value: Any = None,
        user_message: Optional[str] = None,
        error_code: str = "VALIDATION_ERROR",
        context: Optional[Dict[str, Any]] = None
    ) -> APIError:
    
        detail = f"Validation failed for field: {field}"
        user_msg = user_message or f"Invalid value provided for {field}"
        
        return APIError(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            user_message=user_msg,
            log_level=ErrorLevel.WARNING,
            error_code=error_code,
            context=context or {"field": field, "value": value}
        )
    
    @staticmethod
    def unauthorized(
        user_message: Optional[str] = None,
        error_code: str = "UNAUTHORIZED",
        context: Optional[Dict[str, Any]] = None
    ) -> APIError:

        detail = "Authentication required"
        user_msg = user_message or "You must be authenticated to access this resource"
        
        return APIError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            user_message=user_msg,
            log_level=ErrorLevel.WARNING,
            error_code=error_code,
            context=context,
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    @staticmethod
    def forbidden(
        user_message: Optional[str] = None,
        error_code: str = "FORBIDDEN",
        context: Optional[Dict[str, Any]] = None
    ) -> APIError:
        
        detail = "Access forbidden"
        user_msg = user_message or "You don't have permission to access this resource"
        
        return APIError(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            user_message=user_msg,
            log_level=ErrorLevel.WARNING,
            error_code=error_code,
            context=context
        )
    
    @staticmethod
    def internal_server_error(
        user_message: Optional[str] = None,
        log_message: Optional[str] = None,
        error_code: str = "internal_server_error",
        context: Optional[Dict[str, Any]] = None
    ) -> APIError:
        
        detail = "Internal server error occurred"
        user_msg = user_message or "An unexpected error occurred. Please try again later"
        
        return APIError(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            user_message=user_msg,
            log_level=ErrorLevel.ERROR,
            log_message=log_message,
            error_code=error_code,
            context=context
        )
    
    @staticmethod
    def bad_request(
        message: str,
        user_message: Optional[str] = None,
        error_code: str = "BAD_REQUEST",
        context: Optional[Dict[str, Any]] = None
    ) -> APIError:
        user_msg = user_message or message
        
        return APIError(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
            user_message=user_msg,
            log_level=ErrorLevel.WARNING,
            error_code=error_code,
            context=context
        )
    
    @staticmethod
    def conflict(
        resource: str,
        user_message: Optional[str] = None,
        error_code: str = "RESOURCE_CONFLICT",
        context: Optional[Dict[str, Any]] = None
    ) -> APIError:

        detail = f"Conflict with existing {resource}"
        user_msg = user_message or f"The {resource.lower()} already exists or conflicts with existing data"
        
        return APIError(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            user_message=user_msg,
            log_level=ErrorLevel.WARNING,
            error_code=error_code,
            context=context or {"resource": resource}
        )
