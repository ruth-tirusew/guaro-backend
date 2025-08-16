from fastapi import HTTPException, status
from app.adapters.authentication import errors

def handle_auth_exceptions(func):    
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            match type(e):
                case errors.InvalidCredentialsError:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid credentials"
                    ) from e
                
                case errors.TokenVerificationError:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid or expired token"
                    ) from e
                
                case errors.TokenRefreshError:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid refresh token"
                    ) from e
                
                case errors.UserNotFoundError:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="User not found"
                    ) from e
                
                case errors.UserCreationError:
                    raise HTTPException(
                            status_code=status.HTTP_409_CONFLICT,
                            detail=str(e)
                        ) from e
                   
                case errors.UserUpdateError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Failed to update user"
                    ) from e
                
                case errors.ExternalServiceUnavailableError:
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail="Authentication service temporarily unavailable"
                    ) from e
                
                case errors.AuthenticationAdapterError:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Authentication service error"
                    ) from e
                
                case _:
                    raise
    
    return wrapper
