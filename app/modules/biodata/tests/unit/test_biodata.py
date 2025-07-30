# app/modules/biodata/tests/unit/test_biodata_service.py

import pytest
from unittest.mock import Mock, create_autospec
from typing import List, Optional
import uuid
from datetime import datetime

from app.adapters.biodata.models import Crop, InitialBiodata, CropWarehouse
from app.adapters.user.models import UserModel
from app.adapters.product.models import Product, ProductCrop
from app.adapters.resource.models import Resource
from app.adapters.role.models import Role, UserRole
from app.adapters.warehouse.models import Warehouse

from app.modules.biodata.service import BiodataService
from app.adapters.biodata.interface import IBiodataRepository
from app.modules.biodata.schemas import (
    CropCreate, CropUpdate, CropRead,
    InitialBiodataCreate, InitialBiodataUpdate, InitialBiodataRead
)

# --- Fixtures ---

@pytest.fixture
def mock_biodata_repository():
    """Provides a mock instance of IBiodataRepository."""
    return create_autospec(IBiodataRepository, instance=True)

@pytest.fixture
def mock_farmer_service():
    return Mock()

@pytest.fixture
def biodata_service(mock_biodata_repository, mock_farmer_service):
    """
    Fixture to create the BiodataService instance using the mock adapters.
    """
    service = BiodataService(
        farmer_service=mock_farmer_service,
        biodata_repository=mock_biodata_repository
    )
    return service

# --- Sample Data Fixtures ---

@pytest.fixture
def sample_crop_create_data():
    """Provides sample data for creating a Crop."""
    return CropCreate(
        name="Teff",
        variety="Improved White"
    )

@pytest.fixture
def sample_crop_model():
    """Provides a sample Crop model instance (as returned by repository)."""

    return Crop(
        id=uuid.uuid4(),
        name="Teff",
        variety="Improved White",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

@pytest.fixture
def sample_crop_read_data(sample_crop_model):
    """Provides a sample CropRead schema instance."""
    return CropRead.model_validate(sample_crop_model)

@pytest.fixture
def sample_initial_biodata_create_data():
    """Provides sample data for creating InitialBiodata."""
    farmer_id = uuid.uuid4()
    crop_id = uuid.uuid4()
    return InitialBiodataCreate(
        farmer_id=farmer_id,
        crop_id=crop_id,
        average_yield_kg=1000,
        last_harvest_date=datetime.now(),
    )

@pytest.fixture
def sample_initial_biodata_model():
    """Provides a sample InitialBiodata model instance (as returned by repository)."""
    return InitialBiodata(
        id=uuid.uuid4(),
        farmer_id=uuid.uuid4(),
        crop_id=uuid.uuid4(),
        average_yield_kg=1000,
        last_harvest_date=datetime.now(),
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

@pytest.fixture
def sample_initial_biodata_read_data(sample_initial_biodata_model):
    """Provides a sample InitialBiodataRead schema instance."""
    return InitialBiodataRead.model_validate(sample_initial_biodata_model)

@pytest.fixture
def sample_farmer_read():
    mock_farmer = Mock()
    mock_farmer.id = "test-farmer-id-for-mocking"
    return mock_farmer

# --- Test Cases ---

class TestBiodataService:

    # --- Initialization Test ---

    def test_init(self, mock_biodata_repository, mock_farmer_service):
        """Test that the service initializes with the adapters."""
        service = BiodataService(
            farmer_service=mock_farmer_service,
            biodata_repository=mock_biodata_repository
        )
        assert service.repository == mock_biodata_repository
        assert service.farmer_service == mock_farmer_service

    # --- Crop Tests ---

    def test_create_crop(self, biodata_service, mock_biodata_repository, sample_crop_create_data, sample_crop_model, sample_crop_read_data):
        """Test creating a crop successfully."""
        # Arrange
        mock_biodata_repository.create_crop.return_value = sample_crop_model

        # Act
        result = biodata_service.create_crop(sample_crop_create_data)

        # Assert
        mock_biodata_repository.create_crop.assert_called_once_with(sample_crop_create_data.model_dump())
        assert result == sample_crop_read_data

    def test_get_crop_by_id_found(self, biodata_service, mock_biodata_repository, sample_crop_model, sample_crop_read_data):
        """Test retrieving a crop by ID when it exists."""
        # Arrange
        crop_id = sample_crop_model.id
        mock_biodata_repository.get_crop_by_id.return_value = sample_crop_model

        # Act
        result = biodata_service.get_crop_by_id(crop_id)

        # Assert
        mock_biodata_repository.get_crop_by_id.assert_called_once_with(crop_id)
        assert result == sample_crop_read_data

    def test_get_crop_by_id_not_found(self, biodata_service, mock_biodata_repository):
        """Test retrieving a crop by ID when it does not exist."""
        # Arrange
        crop_id = uuid.uuid4()
        mock_biodata_repository.get_crop_by_id.return_value = None

        # Act
        result = biodata_service.get_crop_by_id(crop_id)

        # Assert
        mock_biodata_repository.get_crop_by_id.assert_called_once_with(crop_id)
        assert result is None

    def test_get_all_crops(self, biodata_service, mock_biodata_repository, sample_crop_model):
        """Test retrieving all crops."""
        # Arrange
        crop_model_2 = Crop(
            id=uuid.uuid4(), name="Maize", variety="Hybrid", created_at=datetime.now(), updated_at=datetime.now()
        )
        crop_models = [sample_crop_model, crop_model_2]
        mock_biodata_repository.get_all_crops.return_value = crop_models

        expected_crop_read_1 = CropRead.model_validate(sample_crop_model)
        expected_crop_read_2 = CropRead.model_validate(crop_model_2)
        expected_crop_reads = [expected_crop_read_1, expected_crop_read_2]

        # Act
        result = biodata_service.get_all_crops()

        # Assert
        mock_biodata_repository.get_all_crops.assert_called_once()
        assert result == expected_crop_reads

    def test_update_crop_success(self, biodata_service, mock_biodata_repository, sample_crop_model, sample_crop_read_data):
        """Test updating a crop successfully."""
        # Arrange
        crop_id = sample_crop_model.id
        update_data = CropUpdate(name=sample_crop_model.name, variety="New Variety")
        updated_model = sample_crop_model
        updated_model.variety = "New Variety"
        mock_biodata_repository.update_crop.return_value = updated_model

        expected_result = CropRead.model_validate(updated_model)

        # Act
        result = biodata_service.update_crop(crop_id, update_data)

        # Assert
        mock_biodata_repository.update_crop.assert_called_once_with(crop_id, update_data.model_dump(exclude_unset=True))
        assert result == expected_result

    def test_update_crop_not_found(self, biodata_service, mock_biodata_repository):
        """Test updating a crop that does not exist."""
        # Arrange
        crop_id = uuid.uuid4()
        update_data = CropUpdate(name=sample_crop_model.name,variety="New Variety")
        mock_biodata_repository.update_crop.return_value = None

        # Act
        result = biodata_service.update_crop(crop_id, update_data)

        # Assert
        mock_biodata_repository.update_crop.assert_called_once_with(crop_id, update_data.model_dump(exclude_unset=True))
        assert result is None

    def test_delete_crop_success(self, biodata_service, mock_biodata_repository):
        """Test deleting a crop successfully."""
        # Arrange
        crop_id = uuid.uuid4()
        mock_biodata_repository.delete_crop.return_value = True

        # Act
        result = biodata_service.delete_crop(crop_id)

        # Assert
        mock_biodata_repository.delete_crop.assert_called_once_with(crop_id)
        assert result is True

    def test_delete_crop_not_found(self, biodata_service, mock_biodata_repository):
        """Test deleting a crop that does not exist."""
        # Arrange
        crop_id = uuid.uuid4()
        mock_biodata_repository.delete_crop.return_value = False

        # Act
        result = biodata_service.delete_crop(crop_id)

        # Assert
        mock_biodata_repository.delete_crop.assert_called_once_with(crop_id)
        assert result is False

    # --- InitialBiodata Tests ---

    def test_create_initial_biodata_success(
        self, biodata_service, mock_biodata_repository,
        mock_farmer_service,
        sample_initial_biodata_create_data,
        sample_initial_biodata_model,
        sample_initial_biodata_read_data,
        sample_farmer_read 
    ):
        """Test creating initial biodata successfully with valid farmer."""
        # Arrange
        farmer_id_str = str(sample_initial_biodata_create_data.farmer_id)
        mock_farmer_service.get_farmer.return_value = sample_farmer_read
        mock_biodata_repository.create_initial_biodata.return_value = sample_initial_biodata_model

        # Act
        result = biodata_service.create_initial_biodata(sample_initial_biodata_create_data)

        # Assert
        mock_farmer_service.get_farmer.assert_called_once_with(farmer_id_str)
        mock_biodata_repository.create_initial_biodata.assert_called_once_with(sample_initial_biodata_create_data.model_dump())
        assert result == sample_initial_biodata_read_data

    def test_create_initial_biodata_farmer_not_found(
        self, biodata_service,
        mock_farmer_service, # Use the isolated mock
        sample_initial_biodata_create_data
    ):
        """Test creating initial biodata fails if farmer does not exist."""
        # Arrange
        farmer_id_str = str(sample_initial_biodata_create_data.farmer_id)
        # *** Key Isolation: Configure the *mock* FarmerService to return None ***
        mock_farmer_service.get_farmer.return_value = None # Simulate farmer not found

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            biodata_service.create_initial_biodata(sample_initial_biodata_create_data)

        assert f"Farmer with id {farmer_id_str} does not exist" in str(exc_info.value)
        # *** Key Isolation: Verify the call was made to the *mock* FarmerService ***
        mock_farmer_service.get_farmer.assert_called_once_with(farmer_id_str)


    def test_get_initial_biodata_by_id_found(
        self, biodata_service, mock_biodata_repository, sample_initial_biodata_model, sample_initial_biodata_read_data
    ):
        """Test retrieving initial biodata by ID when it exists."""
        # Arrange
        biodata_id = sample_initial_biodata_model.id
        mock_biodata_repository.get_initial_biodata_by_id.return_value = sample_initial_biodata_model

        # Act
        result = biodata_service.get_initial_biodata_by_id(biodata_id)

        # Assert
        mock_biodata_repository.get_initial_biodata_by_id.assert_called_once_with(biodata_id)
        assert result == sample_initial_biodata_read_data

    def test_get_initial_biodata_by_id_not_found(self, biodata_service, mock_biodata_repository):
        """Test retrieving initial biodata by ID when it does not exist."""
        # Arrange
        biodata_id = uuid.uuid4()
        mock_biodata_repository.get_initial_biodata_by_id.return_value = None

        # Act
        result = biodata_service.get_initial_biodata_by_id(biodata_id)

        # Assert
        mock_biodata_repository.get_initial_biodata_by_id.assert_called_once_with(biodata_id)
        assert result is None

    def test_get_initial_biodata_by_farmer(self, biodata_service, mock_biodata_repository, sample_initial_biodata_model):
        """Test retrieving initial biodata by farmer ID."""
        # Arrange
        farmer_id = uuid.uuid4()
      
        biodata_model_1 = sample_initial_biodata_model 

        biodata_model_2 = InitialBiodata(
            id=uuid.uuid4(), 
            farmer_id=farmer_id, 
            crop_id=uuid.uuid4(),
            average_yield_kg=6000,
            last_harvest_date=datetime.now(),
            created_at=datetime.now(), 
            updated_at=datetime.now()
        )
        biodata_models = [biodata_model_1, biodata_model_2]
        mock_biodata_repository.get_initial_biodata_by_farmer.return_value = biodata_models

        expected_read_1 = InitialBiodataRead.model_validate(biodata_model_1)
        expected_read_2 = InitialBiodataRead.model_validate(biodata_model_2)
        expected_reads = [expected_read_1, expected_read_2]

        # Act
        result = biodata_service.get_initial_biodata_by_farmer(farmer_id)

        # Assert
        mock_biodata_repository.get_initial_biodata_by_farmer.assert_called_once_with(farmer_id)
        assert result == expected_reads

    def test_get_initial_biodata_by_crop(self, biodata_service, mock_biodata_repository, sample_initial_biodata_model):
        """Test retrieving initial biodata by crop ID."""
        # Arrange
        crop_id = uuid.uuid4()
        biodata_model_1 = sample_initial_biodata_model 
        biodata_model_2 = InitialBiodata(
            id=uuid.uuid4(), 
            farmer_id=uuid.uuid4(), 
            crop_id=crop_id,  
            average_yield_kg=1000,
            last_harvest_date=datetime.now(),
            created_at=datetime.now(), updated_at=datetime.now()
        )
        biodata_models = [biodata_model_1, biodata_model_2]
        mock_biodata_repository.get_initial_biodata_by_crop.return_value = biodata_models

        expected_read_1 = InitialBiodataRead.model_validate(biodata_model_1)
        expected_read_2 = InitialBiodataRead.model_validate(biodata_model_2)
        expected_reads = [expected_read_1, expected_read_2]

        # Act
        result = biodata_service.get_initial_biodata_by_crop(crop_id)

        # Assert
        mock_biodata_repository.get_initial_biodata_by_crop.assert_called_once_with(crop_id)
        assert result == expected_reads

    def test_update_initial_biodata_success(
        self, biodata_service, mock_biodata_repository, sample_initial_biodata_model, sample_initial_biodata_read_data
    ):
        """Test updating initial biodata successfully."""
        # Arrange
        biodata_id = sample_initial_biodata_model.id
        update_data = InitialBiodataUpdate(expected_yield=2500.0)
        updated_model = sample_initial_biodata_model
        updated_model.expected_yield = 2500.0
        mock_biodata_repository.update_initial_biodata.return_value = updated_model

        expected_result = InitialBiodataRead.model_validate(updated_model)

        # Act
        result = biodata_service.update_initial_biodata(biodata_id, update_data)

        # Assert
        mock_biodata_repository.update_initial_biodata.assert_called_once_with(
            biodata_id, update_data.model_dump(exclude_unset=True)
        )
        assert result == expected_result

    def test_update_initial_biodata_not_found(self, biodata_service, mock_biodata_repository):
        """Test updating initial biodata that does not exist."""
        # Arrange
        biodata_id = uuid.uuid4()
        update_data = InitialBiodataUpdate(expected_yield=2500.0)
        mock_biodata_repository.update_initial_biodata.return_value = None

        # Act
        result = biodata_service.update_initial_biodata(biodata_id, update_data)

        # Assert
        mock_biodata_repository.update_initial_biodata.assert_called_once_with(
            biodata_id, update_data.model_dump(exclude_unset=True)
        )
        assert result is None

    def test_delete_initial_biodata_success(self, biodata_service, mock_biodata_repository):
        """Test deleting initial biodata successfully."""
        # Arrange
        biodata_id = uuid.uuid4()
        mock_biodata_repository.delete_initial_biodata.return_value = True

        # Act
        result = biodata_service.delete_initial_biodata(biodata_id)

        # Assert
        mock_biodata_repository.delete_initial_biodata.assert_called_once_with(biodata_id)
        assert result is True

    def test_delete_initial_biodata_not_found(self, biodata_service, mock_biodata_repository):
        """Test deleting initial biodata that does not exist."""
        # Arrange
        biodata_id = uuid.uuid4()
        mock_biodata_repository.delete_initial_biodata.return_value = False # Repository indicates failure/not found

        # Act
        result = biodata_service.delete_initial_biodata(biodata_id)

        # Assert
        mock_biodata_repository.delete_initial_biodata.assert_called_once_with(biodata_id)
        assert result is False

    # --- Exception Handling Tests ---

    def test_create_crop_repository_exception(self, biodata_service, mock_biodata_repository, sample_crop_create_data):
        """Test create_crop handles repository exceptions."""
        # Arrange
        mock_biodata_repository.create_crop.side_effect = Exception("Database connection failed")

        # Act & Assert
        with pytest.raises(Exception, match="Database connection failed"):
            biodata_service.create_crop(sample_crop_create_data)

    def test_get_crop_by_id_repository_exception(self, biodata_service, mock_biodata_repository):
        """Test get_crop_by_id handles repository exceptions."""
        # Arrange
        crop_id = uuid.uuid4()
        mock_biodata_repository.get_crop_by_id.side_effect = Exception("Database query error")

        # Act & Assert
        with pytest.raises(Exception, match="Database query error"):
            biodata_service.get_crop_by_id(crop_id)

