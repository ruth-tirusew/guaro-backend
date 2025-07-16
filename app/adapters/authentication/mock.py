
from app.adapters.authentication.interface import *
from app.logging import logger
from typing import Dict, Any

class MockAuthAdapter(AuthAdapterInterface):
    def __init__(self):
        self._users = {
            "user1": {
                "id": "1",
                "username": "user1",
                "password": "pass1",
                "email": "user1@example.com",
                "first_name": "User",
                "last_name": "One",
                "roles": ["user"]
            }
        }
        self._tokens = {}

    def authenticate(self, credentials: UserCredentials) -> TokenResponse:
        user = self._users.get(credentials.username)
        if user and user["password"] == credentials.password:
            access_token = f"mock-access-token-{user['id']}"
            refresh_token = f"mock-refresh-token-{user['id']}"
            self._tokens[access_token] = user["id"]
            return TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=3600
            )
        raise Exception("Invalid credentials")

    def get_user(self, user_id: str) -> UserInfo:
        for user in self._users.values():
            if user["id"] == user_id:
                return UserInfo(
                    id=user["id"],
                    username=user["username"],
                    email=user["email"],
                    first_name=user["first_name"],
                    last_name=user["last_name"],
                    roles=user["roles"]
                )
        raise Exception("User not found")

    def signout(self, token: str) -> bool:
        if token in self._tokens:
            del self._tokens[token]
            return True
        return False

    def create_auth_client(self):
        return self  

    def verify_token(self, token: str) -> Dict[str, Any]:
        if token in self._tokens:
            user_id = self._tokens[token]
            return {"user_id": user_id, "token": token}
        raise Exception("Invalid token") 