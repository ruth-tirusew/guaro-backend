from datetime import datetime
from enum import Enum as PyEnum
from pydantic import BaseModel as PydanticBaseModel, HttpUrl
from typing import Optional
from uuid import UUID



class EmployeeStatus(str, PyEnum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"
    TERMINATED = "TERMINATED"

class EmployeeType(str, PyEnum):
    FULL_TIME = "FULL_TIME"
    PART_TIME = "PART_TIME"
    CONTRACTOR = "CONTRACTOR"
    INTERN = "INTERN"

class EmployeeProfileDBSchema(PydanticBaseModel):
    id: Optional[str] = None
    image_url: Optional[HttpUrl] = None
    employee_id: str
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    email: str
    phone_number: str
    emergency_contact: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    employee_type: EmployeeType
    department_id: Optional[str] = None
    position: str
    hire_date: datetime
    termination_date: Optional[datetime] = None
    status: EmployeeStatus = EmployeeStatus.ACTIVE
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    national_id: Optional[str] = None
    passport_number: Optional[str] = None

    salary: Optional[float] = None
    currency: str = "ETB"
    bank_name: Optional[str] = None
    bank_account_number: Optional[str] = None
    notes: Optional[str] = None
    is_active: bool = True
    user_id: Optional[str] = None
    hired_by_id: Optional[str] = None
    warehouse_id: Optional[str] = None

    model_config = {"from_attributes": True}


class EmployeeDocumentDBSchema(PydanticBaseModel):
    id: Optional[str] = None
    employee_id: str
    document_type: str
    document_title: str
    document_url: Optional[HttpUrl] = None
    file_path: Optional[str] = None
    issue_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    is_verified: bool = False
    notes: Optional[str] = None

    model_config = {"from_attributes": True}


class EmployeePerformanceReviewDBSchema(PydanticBaseModel):
    id: Optional[str] = None
    employee_id: str
    reviewer_id: str
    review_date: datetime
    review_period_start: datetime
    review_period_end: datetime
    overall_rating: Optional[int] = None
    comments: Optional[str] = None
    goals_achieved: Optional[str] = None
    areas_for_improvement: Optional[str] = None
    next_review_date: Optional[datetime] = None

    model_config = {"from_attributes": True}


class EmployeeSalaryLedgerDBSchema(PydanticBaseModel):
    id: Optional[str] = None
    employee_id: str
    previous_salary: float
    updated_salary: float
    effective_date: datetime
    reason: Optional[str] = None
    approved_by: Optional[str] = None
    approval_date: Optional[datetime] = None
    notes: Optional[str] = None

    model_config = {"from_attributes": True}


class EmployeeLeaveDBSchema(PydanticBaseModel):
    id: Optional[str] = None
    employee_id: str
    leave_type: str
    start_date: datetime
    end_date: datetime
    days_requested: int
    reason: Optional[str] = None
    status: str = "PENDING"
    approved_by: Optional[str] = None
    approval_date: Optional[datetime] = None
    notes: Optional[str] = None

    model_config = {"from_attributes": True}
