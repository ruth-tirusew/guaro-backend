from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional
from uuid import UUID

from app.modules.tax_and_charge.service import TaxService
from app.modules.tax_and_charge.schemas import (
    TaxCreate,
    TaxUpdate,
    Tax,
    TaxList,
    TaxType
)
from app.dependencies import TaxServiceDep 

router = APIRouter(
    prefix="/taxes",
    tags=["Taxes"],
    responses={404: {"description": "Not found"}}
)

@router.post(
    "/",
    response_model=Tax,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new tax",
    description="Create a new tax with the provided information"
)
async def create_tax(
    tax_data: TaxCreate,
    tax_service: TaxServiceDep
) -> Tax:
    """Create a new tax"""
    return tax_service.create_tax(tax_data)

@router.get(
    "/",
    response_model=TaxList,
    summary="List all taxes",
    description="Get a list of all taxes with optional filtering"
)
async def list_taxes(
    tax_service: TaxServiceDep
) -> TaxList:
    """List taxes with optional filtering and pagination"""
    return tax_service.list_taxes()

@router.get(
    "/{tax_id}",
    response_model=Tax,
    summary="Get tax by ID",
    description="Retrieve a specific tax by its ID"
)
async def get_tax(
    tax_id: UUID,
    tax_service: TaxServiceDep
) -> Tax:
    """Get a tax by ID"""
    return tax_service.get_tax_by_id(tax_id)

@router.patch(
    "/{tax_id}",
    response_model=Tax,
    summary="Update tax",
    description="Update an existing tax with partial data"
)
async def update_tax(
    tax_id: UUID,
    tax_data: TaxUpdate,
    tax_service: TaxServiceDep
) -> Tax:
    """Update an existing tax"""
    return tax_service.update_tax(tax_id, tax_data)

@router.delete(
    "/{tax_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete tax",
    description="Soft delete a tax"
)
async def delete_tax(
    tax_id: UUID,
    tax_service: TaxServiceDep
) -> None:
    """Delete a tax"""
    tax_service.delete_tax(tax_id)

@router.get(
    "/search/",
    response_model=List[Tax],
    summary="Search taxes",
    description="Search taxes by name or description"
)
async def search_taxes(
    tax_service: TaxServiceDep,
    q: str = Query(..., min_length=2, description="Search query (minimum 2 characters)"),
) -> List[Tax]:
    """Search taxes by name or description"""
    return tax_service.search_taxes(q)