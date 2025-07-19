from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID
from app.adapters.biodata.models import Crop, InitialBiodata

class IBiodataRepository(ABC):
    # Crop methods
    @abstractmethod
    def create_crop(self, crop_data: dict) -> Crop:
        pass

    @abstractmethod
    def get_crop_by_id(self, crop_id: UUID) -> Optional[Crop]:
        pass

    @abstractmethod
    def get_all_crops(self) -> List[Crop]:
        pass

    @abstractmethod
    def update_crop(self, crop_id: UUID, update_data: dict) -> Optional[Crop]:
        pass

    @abstractmethod
    def delete_crop(self, crop_id: UUID) -> bool:
        pass

    @abstractmethod
    def create_initial_biodata(self, biodata_data: dict) -> InitialBiodata:
        pass

    @abstractmethod
    def get_initial_biodata_by_id(self, biodata_id: UUID) -> Optional[InitialBiodata]:
        pass

    @abstractmethod
    def get_initial_biodata_by_farmer(self, farmer_id: UUID) -> List[InitialBiodata]:
        pass

    @abstractmethod
    def get_initial_biodata_by_crop(self, crop_id: UUID) -> List[InitialBiodata]:
        pass

    @abstractmethod
    def update_initial_biodata(self, biodata_id: UUID, update_data: dict) -> Optional[InitialBiodata]:
        pass

    @abstractmethod
    def delete_initial_biodata(self, biodata_id: UUID) -> bool:
        pass
