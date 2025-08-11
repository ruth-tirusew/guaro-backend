from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from uuid import UUID

from app.modules.farmers.service import FarmerService
from app.modules.farmers.schemas import (
    FarmerCreate, FarmerUpdate, FarmerRead, FarmerList,
    AddressCreate, AddressUpdate, AddressRead, AddressList,
    LegalDocumentCreate, LegalDocumentUpdate, LegalDocumentRead, LegalDocumentList,
    FarmerDetailResponse
)
from app.dependencies import FarmerServiceDep

router = APIRouter(prefix="/farmers", tags=["Farmers"])


@router.get("/details/{id}", response_model=Optional[FarmerRead])
def get_farmer_by_id(id: UUID, farmer_service:FarmerServiceDep):
    print(id)
    return farmer_service.get_farmer(id)

@router.get("", response_model=FarmerList)
def get_all_farmers(farmer_service:FarmerServiceDep):
    return farmer_service.list_farmers()

@router.get("/filter-by-name", response_model=FarmerList)
def search_farmers_by_name(farmer_service:FarmerServiceDep, name: str =Query()):
    return farmer_service.search_farmers_by_name(name)

@router.get("/filter-by-date-range", response_model=FarmerList)
def get_farmers_by_registration_date_range(farmer_service:FarmerServiceDep, start_date: datetime=Query(), end_date: datetime=Query()):
    return farmer_service.get_farmers_by_registration_date_range(start_date=start_date, end_date=end_date)

@router.post("", response_model=FarmerRead)
def create_farmer(farmer_data: FarmerCreate, farmer_service:FarmerServiceDep):
    return farmer_service.create_farmer(farmer_data=farmer_data)

@router.put("/", response_model=FarmerRead)
def update_farmer(farmer_data: FarmerUpdate, farmer_service:FarmerServiceDep):
    return farmer_service.update_farmer(farmer_data)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_farmer(id: str, farmer_service:FarmerServiceDep):
    return farmer_service.delete_farmer(id)

@router.put("/{id}/activate")
def activate_farmer(id: UUID, farmer_service:FarmerServiceDep):
    return farmer_service.activate_farmer(id)

@router.put("/{id}/deactivate")
def deactivate_farmer(id: UUID, farmer_service:FarmerServiceDep):
    return farmer_service.deactivate_farmer(id)

