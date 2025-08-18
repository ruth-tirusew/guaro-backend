import pytest
from testcontainers.keycloak import KeycloakContainer

from app.modules.authentication.service import AuthenticationService
from app.adapters.authentication.keycloak import KeycloakAdapter
from app.modules.authentication.schemas import CreateUserModel, UpdateUserModel
from app.adapters.authentication.interface import UserCredentials, UserInfo

from app.logging import logging

# --- Configuration for the test realm, client, and user ---
TEST_REALM = "test-realm"
TEST_CLIENT_ID = "test-client"
TEST_CLIENT_SECRET = "test-client-secret"

TEST_USERNAME = "test_user"
TEST_PASSWORD = "test_password123"
TEST_EMAIL = "testuser@example.com"
TEST_FIRST_NAME = "Test"
TEST_LAST_NAME = "User"

UPDATED_EMAIL = "updated_testuser@example.com"
UPDATED_FIRST_NAME = "UpdatedTest"
UPDATED_LAST_NAME = "UpdatedUser"

@pytest.fixture(scope="session")
def keycloak_service():
    """
    Fixture to start and stop the Keycloak container for the entire test session.
    Configures a basic realm, client, and user using the Keycloak Admin API.
    Yields the container object for accessing connection details.
    """
    logging.info("Starting Keycloak container...")
    with KeycloakContainer() as keycloak_container:
        logging.info(f"Keycloak container started. URL: {keycloak_container.get_url()}")

        keycloak_url = keycloak_container.get_url()

        # --- 1. Authenticate as Admin to configure Keycloak ---
        admin_username = keycloak_container.username 
        admin_password = keycloak_container.password 
        admin_realm = "master"

        try:
            admin_client = KeycloakAdmin(
                server_url=keycloak_url,
                username=admin_username,
                password=admin_password,
                realm_name=admin_realm, 
                verify=False
            )
            logging.info("Connected to Keycloak Admin API.")

            realm_payload = {
                "realm": TEST_REALM,
                "enabled": True,
                "displayName": "Test Realm"
            }
            admin_client.create_realm(payload=realm_payload)
            logging.info(f"Realm '{TEST_REALM}' created.")

            admin_client.realm_name = TEST_REALM

            client_payload = {
                "clientId": TEST_CLIENT_ID,
                "enabled": True,
                "clientAuthenticatorType": "client-secret",
                "secret": TEST_CLIENT_SECRET,
                "redirectUris": ["*"],
                "webOrigins": ["*"],
                "protocol": "openid-connect"
            }
            admin_client.create_client(payload=client_payload)
            logging.info(f"Client '{TEST_CLIENT_ID}' created in realm '{TEST_REALM}'.")

            user_payload = {
                "username": TEST_USERNAME,
                "email": TEST_EMAIL,
                "firstName": TEST_FIRST_NAME,
                "lastName": TEST_LAST_NAME,
                "enabled": True,
                "credentials": [
                    {
                        "type": "password",
                        "value": TEST_PASSWORD,
                        "temporary": False
                    }
                ]
            }
            admin_client.create_user(payload=user_payload)
            logging.info(f"User '{TEST_USERNAME}' created in realm '{TEST_REALM}'.")

            users = admin_client.get_users(query={"username": TEST_USERNAME})
            if users:
                user_id = users[0]['id']
                logging.info(f"User ID for '{TEST_USERNAME}': {user_id}")

            else:
                raise RuntimeError(f"Failed to find created user '{TEST_USERNAME}'")


        except Exception as e:
            logging.info(f"Error configuring Keycloak: {e}")
            pytest.fail(f"Keycloak setup failed: {e}")

        yield {
            "container": keycloak_container,
            "url": keycloak_url,
            "realm": TEST_REALM,
            "client_id": TEST_CLIENT_ID,
            "client_secret": TEST_CLIENT_SECRET,
            "test_username": TEST_USERNAME,
            "test_password": TEST_PASSWORD,
            "test_email": TEST_EMAIL,
            "test_first_name": TEST_FIRST_NAME,
            "test_last_name": TEST_LAST_NAME,
            "user_id": user_id
        }

        logging.info("Stopping Keycloak container...")


@pytest.fixture
def auth_service(keycloak_service):
    """
    Fixture to create the AuthenticationService instance using the real Keycloak adapter.
    """
    config = keycloak_service
    keycloak_url = config["url"]
    realm_name = config["realm"]
    client_id = config["client_id"]
    client_secret = config["client_secret"]

    logging.info(f"Initializing KeycloakAdapter with URL: {keycloak_url}, Realm: {realm_name}")
    adapter = KeycloakAdapter(
        server_url=keycloak_url,
        client_id=client_id,
        client_secret=client_secret,
        realm=realm_name
    )

    service = AuthenticationService(adapter=adapter)
    logging.info("AuthenticationService initialized with KeycloakAdapter.")
    return service


# --- Integration Tests ---

def test_authenticate_success(auth_service, keycloak_service):
    """Test successful user authentication with Keycloak."""
    config = keycloak_service
    credentials = UserCredentials(username=config["test_username"], password=config["test_password"])

    logging.info(f"Attempting to authenticate user: {credentials.username}")
    token_response = auth_service.authenticate(credentials)

    assert token_response is not None
    assert token_response.access_token is not None
    assert token_response.refresh_token is not None
    assert isinstance(token_response.expires_in, int)
    assert token_response.expires_in > 0
    logging.info("Authentication successful.")


def test_authenticate_failure_invalid_credentials(auth_service, keycloak_service):
    """Test authentication failure with invalid credentials."""
    config = keycloak_service
    invalid_credentials = UserCredentials(username=config["test_username"], password="wrong_password")

    logging.info(f"Attempting to authenticate user: {invalid_credentials.username} with invalid password")
    with pytest.raises(Exception) as exc_info:
        auth_service.authenticate(invalid_credentials)

    assert exc_info.value.status_code == 401 
    logging.info("Authentication correctly failed for invalid credentials.")


def test_get_user_success(auth_service, keycloak_service):
    """Test retrieving user information after authentication."""
    config = keycloak_service
    user_id = config["user_id"]

    logging.info(f"Attempting to get user info for ID: {user_id}")
    user_info = auth_service.get_user(user_id)

    assert user_info is not None
    assert user_info.id == user_id
    assert user_info.username == config["test_username"]
    assert user_info.email == config["test_email"]
    assert user_info.first_name == config["test_first_name"]
    assert user_info.last_name == config["test_last_name"]
    logging.info(f"User info retrieved successfully for user: {user_info.username}")


def test_verify_token_success(auth_service, keycloak_service):
    """Test verifying a valid access token."""
    config = keycloak_service
    credentials = UserCredentials(username=config["test_username"], password=config["test_password"])
    token_response = auth_service.authenticate(credentials)

    access_token = token_response.access_token
    logging.info(f"Attempting to verify access token for user: {config['test_username']}")
    decoded_payload = auth_service.verify_token(access_token)

    assert decoded_payload is not None
    assert decoded_payload['preferred_username'] == config["test_username"]
    assert 'exp' in decoded_payload 
    logging.info("Token verification successful.")


def test_refresh_token_success(auth_service, keycloak_service):
    """Test refreshing an access token using a refresh token."""
    config = keycloak_service
    credentials = UserCredentials(username=config["test_username"], password=config["test_password"])
    initial_token_response = auth_service.authenticate(credentials)

    refresh_token = initial_token_response.refresh_token
    logging.info(f"Attempting to refresh token for user: {config['test_username']}")
    new_token_response = auth_service.refresh_token(refresh_token)

    assert new_token_response is not None
    assert new_token_response.access_token is not None
    assert new_token_response.refresh_token is not None
    assert new_token_response.access_token != initial_token_response.access_token
    assert isinstance(new_token_response.expires_in, int)
    assert new_token_response.expires_in > 0
    logging.info("Token refresh successful.")


def test_signout_success(auth_service, keycloak_service):
    """Test signing out a user (invalidating token)."""
    config = keycloak_service
    credentials = UserCredentials(username=config["test_username"], password=config["test_password"])
    token_response = auth_service.authenticate(credentials)

    access_token = token_response.access_token
    logging.info(f"Attempting to sign out user: {config['test_username']}")
    result = auth_service.signout(access_token)

    assert result is True
    logging.info("Signout executed successfully (token invalidated or logout request sent).")

def test_create_and_get_user(auth_service):
    """Integration test for creating a new user and then retrieving it."""
    new_username = "new_test_user"
    new_email = "new_test_user@example.com"

    new_user_model = CreateUserModel(
        phone=new_username,
        email=new_email,
        first_name="New",
        last_name="TestUser",
        password="NewUserPass!2024"
    )

    logging.info(f"Attempting to create user: {new_username}")
    # Create user
    created_user_info = auth_service.create_user(new_user_model)
    assert created_user_info is not None
    assert created_user_info.username == new_username
    assert created_user_info.email == new_email
    # Note: password is not returned, so we can't assert it.

    logging.info(f"User '{new_username}' created. Attempting to retrieve...")
    # Retrieve the created user by ID
    retrieved_user_info = auth_service.get_user(created_user_info.id)
    assert retrieved_user_info.id == created_user_info.id
    assert retrieved_user_info.username == created_user_info.username
    assert retrieved_user_info.email == created_user_info.email
    logging.info(f"User '{new_username}' retrieved successfully after creation.")

    adapter = auth_service.adapter
    if hasattr(adapter, 'keycloak_admin'):
        try:
            adapter.keycloak_admin.delete_user(created_user_info.id)
            logging.info(f"User '{new_username}' cleaned up.")
        except Exception as e:
            logging.info(f"Warning: Failed to cleanup user '{new_username}': {e}")


def test_update_user(auth_service, keycloak_service):
    """Integration test for updating an existing user."""
    config = keycloak_service
    user_id = config["user_id"] # Update the user created during setup

    update_user_model = UpdateUserModel(
        id=user_id,
        username=config["test_username"],
        email=UPDATED_EMAIL,
        first_name=UPDATED_FIRST_NAME,
        last_name=UPDATED_LAST_NAME
    )

    logging.info(f"Attempting to update user ID: {user_id}")
    # Update user
    updated_user_info = auth_service.update_user(update_user_model)

    assert updated_user_info is not None
    assert updated_user_info.id == user_id
    assert updated_user_info.email == UPDATED_EMAIL
    assert updated_user_info.first_name == UPDATED_FIRST_NAME
    assert updated_user_info.last_name == UPDATED_LAST_NAME
    logging.info(f"User ID '{user_id}' updated successfully.")

    logging.info(f"Verifying update for user ID: {user_id}")
    retrieved_user_info = auth_service.get_user(user_id)
    assert retrieved_user_info.email == UPDATED_EMAIL
    assert retrieved_user_info.first_name == UPDATED_FIRST_NAME
    assert retrieved_user_info.last_name == UPDATED_LAST_NAME
    logging.info(f"User ID '{user_id}' update verified successfully.")
