import pytest
from unittest.mock import Mock, call
from typing import Dict, Any

from app.modules.authentication.service import AuthenticationService
from app.adapters.authentication.interface import (
    AuthAdapterInterface, 
    UserCredentials, 
    TokenResponse, 
    UserInfo, 
    AuthenticationUserCreate,
    UpdateUserModel as InterfaceUpdateModel
)
from app.modules.authentication.schemas import CreateUserModel, UpdateUserModel, PasswordResetResponse


class TestAuthenticationService:
    
    @pytest.fixture
    def mock_adapter(self):
        """Provides a mock adapter instance."""
        return Mock(spec=AuthAdapterInterface)
    
    @pytest.fixture
    def auth_service(self, mock_adapter: AuthAdapterInterface):
        """Provides an AuthenticationService instance using the mock adapter."""
        return AuthenticationService(adapter=mock_adapter)
    
    @pytest.fixture
    def sample_credentials(self):
        """Provides sample user credentials."""
        return UserCredentials(username="testuser", password="testpass")
    
    @pytest.fixture
    def sample_token_response(self):
        """Provides a sample token response."""
        return TokenResponse(
            access_token="access_token_123",
            refresh_token="refresh_token_123",
            token_type="Bearer",
            expires_in=3600,
        )
    
    @pytest.fixture
    def sample_user_info(self):
        """Provides sample user information."""
        return UserInfo(
            id="user_123",
            username="+1234567890",
            email="test@example.com",
            first_name="Test",
            last_name="User",
            enabled=True
        )
    
    @pytest.fixture
    def sample_create_user_model(self):
        return CreateUserModel(
            phone="+1234567890",
            email="test@example.com",
            first_name="Test",
            last_name="User",
            password="secure_password"
        )
    
    @pytest.fixture
    def sample_update_user_model(self):
        return UpdateUserModel(
            id="user_123",
            phone="+1234567890",
            email="updated@example.com",
            first_name="Updated",
            last_name="User"
        )

    def test_init(self, mock_adapter: AuthAdapterInterface):
        """Test that the service initializes with the adapter."""
        service = AuthenticationService(adapter=mock_adapter)
        assert service.adapter == mock_adapter

    def test_authenticate(self, auth_service: AuthenticationService, mock_adapter: AuthAdapterInterface, sample_credentials, sample_token_response):
        # Arrange
        mock_adapter.authenticate.return_value = sample_token_response
        
        # Act
        result = auth_service.authenticate(sample_credentials)
        
        # Assert
        mock_adapter.authenticate.assert_called_once_with(sample_credentials)
        assert result == sample_token_response

    def test_create_user(self, auth_service: AuthenticationService, mock_adapter: AuthAdapterInterface, sample_create_user_model,  sample_user_info: UserInfo):
        """Test create_user method transforms and calls adapter correctly."""
        # Arrange
        mock_adapter.create_user.return_value = sample_user_info
        
        expected_auth_user = AuthenticationUserCreate(
            username=sample_create_user_model.phone,
            email=sample_create_user_model.email,
            firstName=sample_create_user_model.first_name,
            lastName=sample_create_user_model.last_name,
            enabled=True,
            credentials=[{
                "type": "password",
                "value": sample_create_user_model.password,
                "temporary": False
            }]
        )
        
        # Act
        result = auth_service.create_user(sample_create_user_model)
        
        # Assert
        mock_adapter.create_user.assert_called_once()
        args, _ = mock_adapter.create_user.call_args
        called_auth_user_create = args[0] 
        
        assert isinstance(called_auth_user_create, AuthenticationUserCreate)
        assert called_auth_user_create.username == expected_auth_user.username
        assert called_auth_user_create.email == expected_auth_user.email
        assert called_auth_user_create.firstName == expected_auth_user.firstName
        assert called_auth_user_create.lastName == expected_auth_user.lastName
        assert called_auth_user_create.enabled == expected_auth_user.enabled

        assert called_auth_user_create.credentials == expected_auth_user.credentials
        
        assert result == sample_user_info

    def test_update_user(self, auth_service: AuthenticationService, mock_adapter: AuthAdapterInterface, sample_update_user_model,  sample_user_info: UserInfo):
        """Test update_user method calls adapter and returns result."""
        mock_adapter.update_user.return_value = sample_user_info
        
        # Act
        result = auth_service.update_user(sample_update_user_model)
        
        # Assert
        mock_adapter.update_user.assert_called_once_with(sample_update_user_model)
        assert result == sample_user_info

    def test_get_user(self, auth_service: AuthenticationService, mock_adapter: AuthAdapterInterface,  sample_user_info: UserInfo):
        """Test get_user method calls adapter with correct user_id."""
        # Arrange
        user_id = "user_123"
        mock_adapter.get_user.return_value = sample_user_info
        
        # Act
        result = auth_service.get_user(user_id)
        
        # Assert
        mock_adapter.get_user.assert_called_once_with(user_id)
        assert result == sample_user_info

    def test_refresh_token(self, auth_service: AuthenticationService, mock_adapter: AuthAdapterInterface, sample_token_response):
        """Test refresh_token method calls adapter with refresh token."""
        # Arrange
        refresh_token = "refresh_token_123"
        mock_adapter.refresh_token.return_value = sample_token_response
        
        # Act
        result = auth_service.refresh_token(refresh_token)
        
        # Assert
        mock_adapter.refresh_token.assert_called_once_with(refresh_token)
        assert result == sample_token_response

    def test_signout(self, auth_service: AuthenticationService, mock_adapter: AuthAdapterInterface):
        """Test signout method calls adapter and returns boolean result."""
        # Arrange
        token = "access_token_123"
        mock_adapter.signout.return_value = True 
        
        # Act
        result = auth_service.signout(token)
        
        # Assert
        mock_adapter.signout.assert_called_once_with(token)
        assert result is True

    def test_signout_failure(self, auth_service: AuthenticationService, mock_adapter: AuthAdapterInterface):
        """Test signout method handles adapter returning False."""
        # Arrange
        token = "invalid_or_expired_token"
        mock_adapter.signout.return_value = False
        
        # Act
        result = auth_service.signout(token)
        
        # Assert
        mock_adapter.signout.assert_called_once_with(token)
        assert result is False

    def test_verify_token(self, auth_service: AuthenticationService, mock_adapter: AuthAdapterInterface):
        """Test verify_token method calls adapter and returns dictionary."""
        # Arrange
        token = "access_token_123"
        expected_result = {"user_id": "user_123", "exp": 1234567890, "iss": "test-issuer"}
        mock_adapter.verify_token.return_value = expected_result
        
        # Act
        result = auth_service.verify_token(token)
        
        # Assert
        mock_adapter.verify_token.assert_called_once_with(token)
        assert result == expected_result
        assert isinstance(result, dict)


    def test_reset_password(self, auth_service: AuthenticationService, mock_adapter: AuthAdapterInterface,  sample_user_info: UserInfo):
        reset_token = auth_service.init_reset_token(sample_user_info.email)
        new_password="atotallynewpassword"
        result = auth_service.reset_token(reset_token, new_password)
        if not result:
            raise Exception("Failed to reset token")

        credentials =UserCredentials(username=sample_user_info.username, password=new_password)
        auth_service.authenticate(credentials)
        

    # --- Exception Handling Tests ---

    def test_authenticate_adapter_exception(self, auth_service: AuthenticationService, mock_adapter: AuthAdapterInterface, sample_credentials):
        """Test authenticate method handles adapter exceptions."""
        # Arrange
        mock_adapter.authenticate.side_effect = Exception("Authentication failed due to network error")
        
        # Act & Assert
        with pytest.raises(Exception, match="Authentication failed due to network error"):
            auth_service.authenticate(sample_credentials)

    def test_create_user_adapter_exception(self, auth_service: AuthenticationService, mock_adapter: AuthAdapterInterface, sample_create_user_model):
        """Test create_user method handles adapter exceptions."""
        # Arrange
        mock_adapter.create_user.side_effect = ValueError("User data validation failed")
        
        # Act & Assert
        with pytest.raises(ValueError, match="User data validation failed"):
            auth_service.create_user(sample_create_user_model)


    def test_get_user_adapter_exception(self, auth_service: AuthenticationService, mock_adapter: AuthAdapterInterface):
        """Test get_user method handles adapter exceptions."""
        # Arrange
        user_id = "non_existent_user_456"
        mock_adapter.get_user.side_effect = KeyError("User ID not found in database")
        
        # Act & Assert
        with pytest.raises(KeyError, match="User ID not found in database"):
            auth_service.get_user(user_id)

    def test_refresh_token_adapter_exception(self, auth_service: AuthenticationService, mock_adapter: AuthAdapterInterface):
        """Test refresh_token method handles adapter exceptions."""
        # Arrange
        refresh_token = "expired_or_invalid_refresh_token"
        mock_adapter.refresh_token.side_effect = PermissionError("Refresh token expired")
        
        # Act & Assert
        with pytest.raises(PermissionError, match="Refresh token expired"):
            auth_service.refresh_token(refresh_token)

    def test_signout_adapter_exception(self, auth_service: AuthenticationService, mock_adapter: AuthAdapterInterface):
        """Test signout method handles adapter exceptions."""
        # Arrange
        token = "malformed_token"
        mock_adapter.signout.side_effect = ValueError("Invalid token format")
        
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid token format"):
            auth_service.signout(token)

    def test_verify_token_adapter_exception(self, auth_service: AuthenticationService, mock_adapter: AuthAdapterInterface):
        """Test verify_token method handles adapter exceptions."""
        # Arrange
        token = "tampered_token"
        mock_adapter.verify_token.side_effect = Exception("Token signature verification failed")
        
        # Act & Assert
        with pytest.raises(Exception, match="Token signature verification failed"):
            auth_service.verify_token(token)

        

    # --- Data Validation / Transformation Tests ---

    def test_create_user_with_valid_phone_formats(self, auth_service: AuthenticationService, mock_adapter: AuthAdapterInterface,  sample_user_info: UserInfo):
        """Test create_user with various valid phone number formats."""
        valid_phones = ["+1234567890", "+12345678901", "+999888777666"]
        
        for phone in valid_phones:
            # Arrange
            create_user_model = CreateUserModel(
                phone=phone,
                email="test@example.com",
                first_name="Test",
                last_name="User",
                password="secure_password"
            )
            mock_adapter.create_user.return_value = sample_user_info
            mock_adapter.create_user.reset_mock()
            
            # Act
            result = auth_service.create_user(create_user_model)
            
            # Assert
            mock_adapter.create_user.assert_called_once()
            called_args = mock_adapter.create_user.call_args[0][0]
            assert called_args.username == phone
            assert result == sample_user_info

