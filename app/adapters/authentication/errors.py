class AuthenticationError(Exception):
    """Base exception for authentication-related errors"""
    pass

class AuthenticationAdapterError(AuthenticationError):
    """Base exception for adapter-level errors"""
    def __init__(self, message: str, original_error: Exception = None):
        super().__init__(message)
        self.original_error = original_error

class InvalidCredentialsError(AuthenticationAdapterError):
    """Raised when user credentials are invalid"""
    pass

class TokenVerificationError(AuthenticationAdapterError):
    """Raised when token verification fails"""
    pass

class UserNotFoundError(AuthenticationAdapterError):
    """Raised when user is not found"""
    pass

class UserCreationError(AuthenticationAdapterError):
    """Raised when user creation fails"""
    def __init__(self, message: str, user_data: dict = None, original_error: Exception = None):
        super().__init__(message, original_error)
        self.user_data = user_data or {}

class UserUpdateError(AuthenticationAdapterError):
    """Raised when user update fails"""
    def __init__(self, message: str, user_id: str = None, original_error: Exception = None):
        super().__init__(message, original_error)
        self.user_id = user_id

class TokenRefreshError(AuthenticationAdapterError):
    """Raised when token refresh fails"""
    pass

class ExternalServiceUnavailableError(AuthenticationAdapterError):
    """Raised when external authentication service is unavailable"""
    pass