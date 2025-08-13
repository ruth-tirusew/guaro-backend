import re
import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr, field_validator, model_validator, ValidationInfo
from typing import List, Optional
from enum import Enum

from app.adapters.employee.models import EmployeeStatus, EmployeeType

PHONE_REGEX = re.compile(r"^\+?\d{7,15}$")

# ====================== BASE SCHEMAS ======================

class EmployeeBase(BaseModel):
    employee_id: str
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    email: EmailStr
    phone_number: str
    emergency_contact: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    employee_type: EmployeeType
    department_id:  Optional[str] = None
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
    user_id: Optional[uuid.UUID] = None
    manager_id: Optional[uuid.UUID] = None
    warehouse_id: Optional[uuid.UUID] = None

    @field_validator("first_name", "last_name")
    @classmethod
    def name_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Name must not be empty")
        return v.strip()

    @field_validator("phone_number")
    @classmethod
    def phone_must_be_valid(cls, v):
        if not v or not v.strip():
            raise ValueError("Phone must not be empty")
        if not PHONE_REGEX.match(v):
            raise ValueError("Invalid phone number format")
        return v.strip()

    @field_validator("employee_id")
    @classmethod
    def employee_id_must_be_valid(cls, v):
        if not v or not v.strip():
            raise ValueError("Employee ID must not be empty")
        return v.strip()

    @field_validator("position")
    @classmethod
    def position_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Position must not be empty")
        return v.strip()


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    employee_id: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    middle_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    emergency_contact: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    employee_type: Optional[EmployeeType] = None
    department:  Optional[str] = None
    position: Optional[str] = None
    hire_date: Optional[datetime] = None
    termination_date: Optional[datetime] = None
    status: Optional[EmployeeStatus] = None
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    national_id: Optional[str] = None
    passport_number: Optional[str] = None
    salary: Optional[float] = None
    currency: Optional[str] = None
    bank_name: Optional[str] = None
    bank_account_number: Optional[str] = None
    notes: Optional[str] = None
    user_id: Optional[uuid.UUID] = None
    manager_id: Optional[uuid.UUID] = None
    warehouse_id: Optional[uuid.UUID] = None

    @model_validator(mode="after")
    def at_least_one_field_provided(self):
        fields = [
            self.employee_id, self.first_name, self.last_name, self.middle_name,
            self.email, self.phone_number, self.emergency_contact, self.emergency_contact_name,
            self.employee_type, self.department, self.position, self.hire_date,
            self.termination_date, self.status, self.date_of_birth, self.gender,
            self.national_id, self.passport_number, self.salary, self.currency,
            self.bank_name, self.bank_account_number, self.notes, self.user_id,
            self.manager_id, self.warehouse_id
        ]
        if not any(fields):
            raise ValueError("At least one field must be provided for update")
        return self


class EmployeeRead(EmployeeBase):
    id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    salary_increase_this_month: Optional[float] = None

    model_config = {"from_attributes": True}


class EmployeeList(BaseModel):
    employees: List[EmployeeRead]


# ====================== DOCUMENT SCHEMAS ======================

class EmployeeDocumentBase(BaseModel):
    document_type: str
    document_title: str
    document_url: Optional[str] = None
    file_path: Optional[str] = None
    issue_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    is_verified: bool = False
    notes: Optional[str] = None

    @field_validator("document_type", "document_title")
    @classmethod
    def field_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Field must not be empty")
        return v.strip()


class EmployeeDocumentCreate(EmployeeDocumentBase):
    employee_id: uuid.UUID


class EmployeeDocumentUpdate(BaseModel):
    document_type: Optional[str] = None
    document_title: Optional[str] = None
    document_url: Optional[str] = None
    file_path: Optional[str] = None
    issue_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    is_verified: Optional[bool] = None
    notes: Optional[str] = None

    @model_validator(mode="after")
    def at_least_one_field_provided(self):
        fields = [
            self.document_type, self.document_title, self.document_url,
            self.file_path, self.issue_date, self.expiry_date,
            self.is_verified, self.notes
        ]
        if not any(fields):
            raise ValueError("At least one field must be provided for update")
        return self


class EmployeeDocumentRead(EmployeeDocumentBase):
    id: uuid.UUID
    employee_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class EmployeeDocumentList(BaseModel):
    documents: List[EmployeeDocumentRead]


# ====================== PERFORMANCE REVIEW SCHEMAS ======================

class EmployeePerformanceReviewBase(BaseModel):
    review_date: datetime
    review_period_start: datetime
    review_period_end: datetime
    overall_rating: Optional[int] = None
    comments: Optional[str] = None
    goals_achieved: Optional[str] = None
    areas_for_improvement: Optional[str] = None
    next_review_date: Optional[datetime] = None

    @field_validator("overall_rating")
    @classmethod
    def rating_must_be_valid(cls, v):
        if v is not None and (v < 1 or v > 5):
            raise ValueError("Rating must be between 1 and 5")
        return v


class EmployeePerformanceReviewCreate(EmployeePerformanceReviewBase):
    employee_id: uuid.UUID
    reviewer_id: uuid.UUID


class EmployeePerformanceReviewUpdate(BaseModel):
    review_date: Optional[datetime] = None
    review_period_start: Optional[datetime] = None
    review_period_end: Optional[datetime] = None
    overall_rating: Optional[int] = None
    comments: Optional[str] = None
    goals_achieved: Optional[str] = None
    areas_for_improvement: Optional[str] = None
    next_review_date: Optional[datetime] = None

    @model_validator(mode="after")
    def at_least_one_field_provided(self):
        fields = [
            self.review_date, self.review_period_start, self.review_period_end,
            self.overall_rating, self.comments, self.goals_achieved,
            self.areas_for_improvement, self.next_review_date
        ]
        if not any(fields):
            raise ValueError("At least one field must be provided for update")
        return self


class EmployeePerformanceReviewRead(EmployeePerformanceReviewBase):
    id: uuid.UUID
    employee_id: uuid.UUID
    reviewer_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class EmployeePerformanceReviewList(BaseModel):
    reviews: List[EmployeePerformanceReviewRead]


# ====================== LEAVE SCHEMAS ======================

class EmployeeLeaveBase(BaseModel):
    leave_type: str
    start_date: datetime
    end_date: datetime
    days_requested: int
    reason: Optional[str] = None
    status: str = "PENDING"
    notes: Optional[str] = None

    @field_validator("leave_type")
    @classmethod
    def leave_type_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Leave type must not be empty")
        return v.strip()

    @field_validator("days_requested")
    @classmethod
    def days_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Days requested must be positive")
        return v

    @model_validator(mode="after")
    def end_date_after_start_date(self):
        if self.end_date <= self.start_date:
            raise ValueError("End date must be after start date")
        return self


class EmployeeLeaveCreate(EmployeeLeaveBase):
    employee_id: uuid.UUID


class EmployeeLeaveUpdate(BaseModel):
    leave_type: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    days_requested: Optional[int] = None
    reason: Optional[str] = None
    status: Optional[str] = None
    approved_by: Optional[uuid.UUID] = None
    approval_date: Optional[datetime] = None
    notes: Optional[str] = None

    @model_validator(mode="after")
    def at_least_one_field_provided(self):
        fields = [
            self.leave_type, self.start_date, self.end_date, self.days_requested,
            self.reason, self.status, self.approved_by, self.approval_date, self.notes
        ]
        if not any(fields):
            raise ValueError("At least one field must be provided for update")
        return self


class EmployeeLeaveRead(EmployeeLeaveBase):
    id: uuid.UUID
    employee_id: uuid.UUID
    approved_by: Optional[uuid.UUID] = None
    approval_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class EmployeeLeaveList(BaseModel):
    leaves: List[EmployeeLeaveRead]


# ====================== SALARY LEDGER SCHEMAS ======================

class EmployeeSalaryLedgerBase(BaseModel):
    previous_salary: float
    updated_salary: float
    effective_date: datetime
    reason: Optional[str] = None
    notes: Optional[str] = None

    @field_validator("previous_salary", "updated_salary")
    @classmethod
    def salary_must_be_positive(cls, v):
        if v < 0:
            raise ValueError("Salary must be positive")
        return v


class EmployeeSalaryLedgerCreate(EmployeeSalaryLedgerBase):
    employee_id: uuid.UUID


class EmployeeSalaryLedgerUpdate(BaseModel):
    previous_salary: Optional[float] = None
    updated_salary: Optional[float] = None
    effective_date: Optional[datetime] = None
    reason: Optional[str] = None
    approved_by: Optional[uuid.UUID] = None
    approval_date: Optional[datetime] = None
    notes: Optional[str] = None

    @model_validator(mode="after")
    def at_least_one_field_provided(self):
        fields = [
            self.previous_salary, self.updated_salary, self.effective_date,
            self.reason, self.approved_by, self.approval_date, self.notes
        ]
        if not any(fields):
            raise ValueError("At least one field must be provided for update")
        return self


class EmployeeSalaryLedgerRead(EmployeeSalaryLedgerBase):
    id: uuid.UUID
    employee_id: uuid.UUID
    approved_by: Optional[uuid.UUID] = None
    approval_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class EmployeeSalaryLedgerList(BaseModel):
    salary_ledger: List[EmployeeSalaryLedgerRead]


# ====================== DETAILED RESPONSE SCHEMAS ======================

class EmployeeDetailResponse(BaseModel):
    employee: EmployeeRead
    documents: Optional[EmployeeDocumentList] = None
    performance_reviews: Optional[EmployeePerformanceReviewList] = None
    leave_records: Optional[EmployeeLeaveList] = None
    salary_ledger: Optional[EmployeeSalaryLedgerList] = None
