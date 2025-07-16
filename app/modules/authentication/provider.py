from fastapi import Depends

from app.modules.authentication.service import AuthenticationService
from app.adapters.authentication.interface import AuthAdapterInterface
from app.dependencies import get_auth_adapter

def authentication_service_factory():
    auth_adapter = get_auth_adapter()
    return AuthenticationService(auth_adapter)

def get_authentication_service(auth_service: AuthenticationService = Depends(authentication_service_factory)):
    return auth_service
