from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from uuid import UUID

from app.modules.biodata.service import BiodataService
from app.modules.biodata.schemas import (
    CropCreate,CropUpdate,CropRead,CropList,
    InitialBiodataCreate,InitialBiodataUpdate,InitialBiodataRead, InitialBiodataList,
    GRNRequest
)
from app.dependencies import BiodataServiceDep
from app.utils.middlewares.authorization import require_auth, require_permission


router = APIRouter(prefix="", tags=["Biodata"])

@router.get("/raw-material/{id}", response_model=Optional[CropRead])
def get_raw_material_by_id(id: UUID, biodata_service:BiodataServiceDep):
    return biodata_service.get_crop_by_id(id)

@router.get("/raw-material", response_model=CropList)
def get_all_raw_materials(
    biodata_service:BiodataServiceDep,
    user_info: dict = Depends(require_auth()),
    _=Depends(require_permission("crop", "read"))
):
    return biodata_service.get_all_crops()

@router.post("/raw-material/create", response_model=CropRead)
def create_raw_materials(crop_data: CropCreate, biodata_service:BiodataServiceDep):
    return biodata_service.create_crop(crop_data)

@router.put("/raw-material", response_model=Optional[CropRead])
def update_raw_material(crop_data: CropUpdate, biodata_service:BiodataServiceDep):
    return biodata_service.update_crop(crop_data)

@router.put("/raw-material/receive", response_model=Optional[CropRead])
def receive_raw_material(data: GRNRequest, biodata_service:BiodataServiceDep):
    return biodata_service.receive_crop(data)

@router.put("/raw-material/deplete", response_model=Optional[CropRead])
def deplete_raw_material(data: GRNRequest, biodata_service:BiodataServiceDep):
    return biodata_service.deplete_crop(data)

@router.delete("/raw-material/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_raw_material(id:UUID, biodata_service:BiodataServiceDep):
    return biodata_service.delete_crop(id)

@router.get("/initial-biodata/", response_model=InitialBiodataList, status_code=status.HTTP_200_OK)
def get_initial_biodata_by_farmer(farmer_id: str, biodata_service:BiodataServiceDep):
    return biodata_service.get_initial_biodata_by_farmer(farmer_id=farmer_id)

@router.get("/initial-biodata/{id}", response_model=InitialBiodataList, status_code=status.HTTP_200_OK)
def get_initial_biodata_by_id(id: UUID, biodata_service:BiodataServiceDep):
    return biodata_service.get_initial_biodata_by_id(id=id)

@router.post("/initial-biodata", response_model=Optional[InitialBiodataRead])
def create_initial_biodata(biodata: InitialBiodataCreate, biodata_service:BiodataServiceDep):
    return biodata_service.create_initial_biodata(biodata)
