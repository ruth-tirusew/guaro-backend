import pytest
from app.modules.authentication.service import AuthenticationService
from app.adapters.authentication.interface import UserCredentials
from app.modules.authentication.schemas import CreateUserModel
from app.adapters.authentication.mock import MockAuthAdapter

def test_authenticate():
    service = AuthenticationService(adapter=MockAuthAdapter())
    credentials = UserCredentials(username="user1", password="pass1")
    token = service.authenticate(credentials)
    assert token.access_token.startswith("mock-access-token-")
    assert token.refresh_token.startswith("mock-refresh-token-")

def test_create_user():
    service = AuthenticationService(adapter=MockAuthAdapter())
    user_data = CreateUserModel(
        phone="+251989097890",
        email="newuser@example.com",
        first_name="New",
        last_name="User",
        password="newpass",
        roles=["user"]
    )
    user = service.create_user(user_data)
    assert user.username == "+251989097890"
    assert user.email == "newuser@example.com"
    assert user.first_name == "New"
    assert user.last_name == "User"