from fastapi import APIRouter, Depends, HTTPException, status, Request

from app.modules.authentication.service import AuthenticationService
from app.modules.authentication.schemas import CreateUserModel
from app.adapters.authentication.interface import UserCredentials, TokenResponse, UserInfo, RefreshTokenRequest, AuthenticationUserCreate
from app.modules.authentication.helpers import handle_auth_exceptions
from app.dependencies import AuthServiceDep


router = APIRouter(prefix="/auth", tags=["Authentication"])

@handle_auth_exceptions
@router.post("/login", response_model=TokenResponse)
def login(credentials: UserCredentials, auth_service: AuthServiceDep):
    try:
        return auth_service.authenticate(credentials)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@handle_auth_exceptions
@router.get("/user/{user_id}", response_model=UserInfo)
def get_user(user_id: str, auth_service: AuthServiceDep):
    try:
        return auth_service.get_user(user_id)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@handle_auth_exceptions
@router.post("/refresh", response_model=TokenResponse)
def refresh_token(request: RefreshTokenRequest, auth_service: AuthServiceDep):
    try:
        return auth_service.refresh_token(request.refresh_token)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

@handle_auth_exceptions
@router.post("/logout")
def logout(request: Request, auth_service: AuthServiceDep):
    token = request.headers.get("Authorization")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    token = token.replace("Bearer ", "")
    try:
        result = auth_service.signout(token)
        if not result:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Logout failed")
        return {"detail": "Successfully logged out"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
