from datetime import datetime, timezone
from uuid import uuid4, UUID
from sqlalchemy import Column, String, Integer, Numeric, DateTime, ForeignKey, Boolean, Text, select, func
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.ext.hybrid import hybrid_property

from app.models.base import BaseModel
from app.adapters.employee.schema import(
    EmployeeStatus, 
    EmployeeType
)
from app.logging import logging

class Department(BaseModel):
    __tablename__ = "departments"
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    created_by = Column(PG_UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    updated_by = Column(PG_UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)

    employees = relationship('EmployeeProfile', back_populates='department')


# ====================== EMPLOYEE PROFILE MODELS ======================
class EmployeeProfile(BaseModel):
    __tablename__ = "employee_profiles"
    
    # Basic Information
    image_url = Column(String(500), nullable=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    middle_name = Column(String(100), nullable=True)
    
    # Contact Information
    email = Column(String(255), unique=True, nullable=False)
    phone_number = Column(String(20), unique=True, nullable=False)
    emergency_contact = Column(String(20), nullable=True)
    emergency_contact_name = Column(String(100), nullable=True)
    
    # Employment Details
    employee_type = Column(SQLEnum(EmployeeType), nullable=False)
    department_id = Column(PG_UUID(as_uuid=True), ForeignKey('departments.id'), nullable=False)
    department = relationship('Department', back_populates='employees')
    position = Column(String(100), nullable=False)
    hire_date = Column(DateTime, nullable=False)
    termination_date = Column(DateTime, nullable=True)
    status = Column(SQLEnum(EmployeeStatus), default=EmployeeStatus.ACTIVE)
    
    # Personal Information
    date_of_birth = Column(DateTime, nullable=True)
    gender = Column(String(20), nullable=True)
    national_id = Column(String(50), unique=True, nullable=True)
    passport_number = Column(String(50), unique=True, nullable=True) 
    
    # Financial Information
    salary = Column(Numeric(12, 2), nullable=True)
    currency = Column(String(3), default="ETB")
    bank_name = Column(String(100), nullable=True)
    bank_account_number = Column(String(50), nullable=True)
    
    # Additional Information
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=True)
    user = relationship("UserModel", backref="employee_profile")
        
    hired_by_id = Column(PG_UUID(as_uuid=True), ForeignKey("employee_profiles.id"), nullable=True)
    hired_by = relationship(
        "EmployeeProfile", 
        remote_side="EmployeeProfile.id", 
        backref="hired_employees"
    )
    
    # Document relationships
    documents = relationship("EmployeeDocument", back_populates="employee", cascade="all, delete-orphan")

    # Experience relationships
    experiences = relationship("EmployeeExperience", back_populates="employee", cascade="all, delete-orphan")

    # Education relationships
    educations = relationship("EmployeeEducation", back_populates="employee", cascade="all, delete-orphan")

    # Performance relationships
    performance_reviews = relationship(
        "EmployeePerformanceReview", 
        back_populates="employee", 
        foreign_keys="EmployeePerformanceReview.employee_id",
        cascade="all, delete-orphan"
    )
    reviews_given = relationship(
        "EmployeePerformanceReview", 
        back_populates="reviewer", 
        foreign_keys="EmployeePerformanceReview.reviewer_id",
        cascade="all, delete-orphan"
    )

    # Leave relationships
    leave_records = relationship(
        "EmployeeLeave", 
        back_populates="employee", 
        foreign_keys="EmployeeLeave.employee_id",
        cascade="all, delete-orphan"
    )
    approved_leaves = relationship(
        "EmployeeLeave", 
        back_populates="approver", 
        foreign_keys="EmployeeLeave.approved_by",
        cascade="all, delete-orphan"
    )
    
    # Salary ledger relationships 
    salary_ledger = relationship(
        "EmployeeSalaryLedger", 
        back_populates="employee", 
        foreign_keys="EmployeeSalaryLedger.employee_id",
        cascade="all, delete-orphan"
    )
    approved_salary_ledger = relationship(
        "EmployeeSalaryLedger", 
        back_populates="approver", 
        foreign_keys="EmployeeSalaryLedger.approved_by",
        cascade="all, delete-orphan"
    )
    
    @hybrid_property
    def salary_increase_this_month(self):
        """Return salary increase for the current month (in-memory)."""
        current_month = datetime.now(timezone.utc).month
        current_year = datetime.now(timezone.utc).year
        
        monthly_increases = [
            ledger.updated_salary - ledger.previous_salary 
            for ledger in self.salary_ledger
            if ledger.effective_date.month == current_month and ledger.effective_date.year == current_year
        ]
        return sum(monthly_increases)

    @salary_increase_this_month.expression
    def salary_increase_this_month(cls):
        """SQL expression to calculate salary increase for current month (database-level)."""
        try:
            current_month = datetime.now(timezone.utc).month
            current_year = datetime.now(timezone.utc).year
            
            return (
                select(func.coalesce(func.sum(EmployeeSalaryLedger.updated_salary - EmployeeSalaryLedger.previous_salary), 0.0))
                .where(
                    EmployeeSalaryLedger.employee_id == cls.id,
                    func.extract('month', EmployeeSalaryLedger.effective_date) == current_month,
                    func.extract('year', EmployeeSalaryLedger.effective_date) == current_year
                )
                .label("salary_increase_this_month")
            )
        except Exception as e:
            logging.error(e)


class EmployeeExperience(BaseModel):
    __tablename__ = "employee_experiences"
    
    employee_id = Column(PG_UUID(as_uuid=True), ForeignKey('employee_profiles.id'), nullable=False)
    company_name = Column(String(255), nullable=False)
    position = Column(String(255), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    description = Column(Text, nullable=True)

    employee = relationship("EmployeeProfile", back_populates="experiences")


class EmployeeEducation(BaseModel):
    __tablename__ = "employee_educations"
    
    employee_id = Column(PG_UUID(as_uuid=True), ForeignKey('employee_profiles.id'), nullable=False)
    school_name = Column(String(255), nullable=False)
    degree = Column(String(255), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    description = Column(Text, nullable=True)

    employee = relationship("EmployeeProfile", back_populates="educations")


class EmployeeSalaryLedger(BaseModel):
    __tablename__ = "employee_salary_ledger"
    
    employee_id = Column(PG_UUID(as_uuid=True), ForeignKey("employee_profiles.id"), nullable=False)
    previous_salary = Column(Numeric(12, 2), nullable=False)
    updated_salary = Column(Numeric(12, 2), nullable=False)
    effective_date = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    reason = Column(String(255), nullable=True)
    approved_by = Column(PG_UUID(as_uuid=True), ForeignKey("employee_profiles.id"), nullable=True)
    approval_date = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    
    employee = relationship(
        "EmployeeProfile", 
        back_populates="salary_ledger", 
        foreign_keys=[employee_id]
    )
    approver = relationship(
        "EmployeeProfile", 
        back_populates="approved_salary_ledger", 
        foreign_keys=[approved_by]
    )


class EmployeeDocument(BaseModel):
    __tablename__ = "employee_documents"
    
    employee_id = Column(PG_UUID(as_uuid=True), ForeignKey("employee_profiles.id"), nullable=False)
    document_type = Column(String(100), nullable=False)
    document_title = Column(String(255), nullable=False)
    document_url = Column(String(500), nullable=True)
    file_path = Column(String(500), nullable=True)
    issue_date = Column(DateTime, nullable=True)
    expiry_date = Column(DateTime, nullable=True)
    is_verified = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)
    
    employee = relationship("EmployeeProfile", back_populates="documents")


class EmployeePerformanceReview(BaseModel):
    __tablename__ = "employee_performance_reviews"

    employee_id = Column(PG_UUID(as_uuid=True), ForeignKey("employee_profiles.id"), nullable=False)
    reviewer_id = Column(PG_UUID(as_uuid=True), ForeignKey("employee_profiles.id"), nullable=False)
    review_date = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    review_period_start = Column(DateTime, nullable=False)
    review_period_end = Column(DateTime, nullable=False)
    overall_rating = Column(Integer, nullable=True)
    comments = Column(Text, nullable=True)
    goals_achieved = Column(Text, nullable=True)
    areas_for_improvement = Column(Text, nullable=True)
    next_review_date = Column(DateTime, nullable=True)

    employee = relationship(
        "EmployeeProfile", 
        back_populates="performance_reviews", 
        foreign_keys=[employee_id]
    )
    reviewer = relationship(
        "EmployeeProfile", 
        back_populates="reviews_given", 
        foreign_keys=[reviewer_id]
    )


class EmployeeLeave(BaseModel):
    __tablename__ = "employee_leave"
    
    employee_id = Column(PG_UUID(as_uuid=True), ForeignKey("employee_profiles.id"), nullable=False)
    leave_type = Column(String(50), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    days_requested = Column(Integer, nullable=False)
    reason = Column(Text, nullable=True)
    status = Column(String(20), default="PENDING")
    approved_by = Column(PG_UUID(as_uuid=True), ForeignKey("employee_profiles.id"), nullable=True)
    approval_date = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    
    employee = relationship(
        "EmployeeProfile", 
        back_populates="leave_records", 
        foreign_keys=[employee_id]
    )
    approver = relationship(
        "EmployeeProfile", 
        back_populates="approved_leaves", 
        foreign_keys=[approved_by]
    )