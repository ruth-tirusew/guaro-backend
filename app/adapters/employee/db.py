
from app.adapters.employee.interface import IEmployeeRepository
from app.adapters.employee.models import (
    EmployeeProfile,
    EmployeeDocument,
    EmployeePerformanceReview,
    EmployeeLeave,
    EmployeeSalaryLedger,
    EmployeeStatus,
    EmployeeType,
    Department
)
from app.adapters.employee.schema import (
        EmployeeProfileDBSchema,
    EmployeeDocumentDBSchema,
    EmployeePerformanceReviewDBSchema,
    EmployeeLeaveDBSchema,
    EmployeeSalaryLedgerDBSchema,
)

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_, and_, func
from fastapi import HTTPException, status
import uuid
from datetime import datetime
from typing import Optional, List


class EmployeeRepository(IEmployeeRepository):
    def __init__(self, db_session: Session):
        self.db = db_session

    # ====================== EMPLOYEE PROFILE OPERATIONS ======================

    def create_employee_profile(self, employee_data: EmployeeProfileDBSchema) -> EmployeeProfile:
        employee = EmployeeProfile(**employee_data.dict())
        self.db.add(employee)
        try:
            self.db.commit()
            self.db.refresh(employee)
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Employee profile creation failed.")
        return employee

    def get_employee_by_id(self, employee_id: str) -> Optional[EmployeeProfile]:
        try:
            uuid_obj = uuid.UUID(employee_id)
            return self.db.query(EmployeeProfile).filter(EmployeeProfile.id == uuid_obj).first()
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid employee ID format.")

    def get_employee_by_employee_id(self, employee_id: str) -> Optional[EmployeeProfile]:
        return self.db.query(EmployeeProfile).filter(EmployeeProfile.employee_id == employee_id).first()

    def get_employee_by_email(self, email: str) -> Optional[EmployeeProfile]:
        return self.db.query(EmployeeProfile).filter(EmployeeProfile.email == email).first()

    def get_employee_by_phone(self, phone_number: str) -> Optional[EmployeeProfile]:
        return self.db.query(EmployeeProfile).filter(EmployeeProfile.phone_number == phone_number).first()

    def get_all_employees(self) -> List[EmployeeProfile]:
        return self.db.query(EmployeeProfile).all()

    def update_employee_profile(self, employee_id: str, update_data: EmployeeProfileDBSchema) -> Optional[EmployeeProfile]:
        employee = self.get_employee_by_id(employee_id)
        if not employee:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found.")
        
        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(employee, field, value)
        
        try:
            self.db.commit()
            self.db.refresh(employee)
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Employee profile update failed due to integrity error.")
        return employee

    def delete_employee_profile(self, employee_id: str) -> bool:
        employee = self.get_employee_by_id(employee_id)
        if not employee:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found.")
        employee.is_deleted=True
        self.db.commit()
        return True

    def activate_employee(self, employee_id: str) -> bool:
        employee = self.get_employee_by_id(employee_id)
        if not employee:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found.")
        
        employee.status = EmployeeStatus.ACTIVE
        employee.is_active = True
        self.db.commit()
        return True

    def deactivate_employee(self, employee_id: str) -> bool:
        employee = self.get_employee_by_id(employee_id)
        if not employee:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found.")
        
        employee.status = EmployeeStatus.INACTIVE
        employee.is_active = False
        self.db.commit()
        return True

    # ====================== EMPLOYEE DOCUMENT OPERATIONS ======================

    def create_employee_document(self, document_data: EmployeeDocumentDBSchema) -> EmployeeDocument:
        document = EmployeeDocument(**document_data.dict())
        self.db.add(document)
        try:
            self.db.commit()
            self.db.refresh(document)
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Employee document creation failed.")
        return document

    def get_employee_document_by_id(self, document_id: str) -> Optional[EmployeeDocument]:
        try:
            uuid_obj = uuid.UUID(document_id)
            return self.db.query(EmployeeDocument).filter(EmployeeDocument.id == uuid_obj).first()
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid document ID format.")

    def get_employee_documents_by_employee(self, employee_id: str) -> List[EmployeeDocument]:
        try:
            uuid_obj = uuid.UUID(employee_id)
            return self.db.query(EmployeeDocument).filter(EmployeeDocument.employee_id == uuid_obj).all()
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid employee ID format.")

    def get_employee_documents_by_type(self, employee_id: str, document_type: str) -> List[EmployeeDocument]:
        try:
            uuid_obj = uuid.UUID(employee_id)
            return self.db.query(EmployeeDocument).filter(
                and_(
                    EmployeeDocument.employee_id == uuid_obj,
                    EmployeeDocument.document_type == document_type
                )
            ).all()
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid employee ID format.")

    def update_employee_document(self, document_id: str, update_data: EmployeeDocumentDBSchema) -> Optional[EmployeeDocument]:
        document = self.get_employee_document_by_id(document_id)
        if not document:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee document not found.")
        
        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(document, field, value)
        
        try:
            self.db.commit()
            self.db.refresh(document)
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Employee document update failed due to integrity error.")
        return document

    def delete_employee_document(self, document_id: str) -> bool:
        document = self.get_employee_document_by_id(document_id)
        if not document:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee document not found.")
        document.is_deleted=True
        self.db.commit()
        return True

    # ====================== PERFORMANCE REVIEW OPERATIONS ======================

    def create_performance_review(self, review_data: EmployeePerformanceReviewDBSchema) -> EmployeePerformanceReview:
        review = EmployeePerformanceReview(**review_data.dict())
        self.db.add(review)
        try:
            self.db.commit()
            self.db.refresh(review)
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Performance review creation failed.")
        return review

    def get_performance_review_by_id(self, review_id: str) -> Optional[EmployeePerformanceReview]:
        try:
            uuid_obj = uuid.UUID(review_id)
            return self.db.query(EmployeePerformanceReview).filter(EmployeePerformanceReview.id == uuid_obj).first()
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid review ID format.")

    def get_performance_reviews_by_employee(self, employee_id: str) -> List[EmployeePerformanceReview]:
        try:
            uuid_obj = uuid.UUID(employee_id)
            return self.db.query(EmployeePerformanceReview).filter(EmployeePerformanceReview.employee_id == uuid_obj).all()
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid employee ID format.")

    def update_performance_review(self, review_id: str, update_data: EmployeePerformanceReviewDBSchema) -> Optional[EmployeePerformanceReview]:
        review = self.get_performance_review_by_id(review_id)
        if not review:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Performance review not found.")
        
        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(review, field, value)
        
        try:
            self.db.commit()
            self.db.refresh(review)
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Performance review update failed due to integrity error.")
        return review

    def delete_performance_review(self, review_id: str) -> bool:
        review = self.get_performance_review_by_id(review_id)
        if not review:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Performance review not found.")
        review.is_deleted=True
        self.db.commit()
        return True

    # ====================== LEAVE OPERATIONS ======================

    def create_leave_request(self, leave_data: EmployeeLeaveDBSchema) -> EmployeeLeave:
        leave = EmployeeLeave(**leave_data.dict())
        self.db.add(leave)
        try:
            self.db.commit()
            self.db.refresh(leave)
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Leave request creation failed.")
        return leave

    def get_leave_request_by_id(self, leave_id: str) -> Optional[EmployeeLeave]:
        try:
            uuid_obj = uuid.UUID(leave_id)
            return self.db.query(EmployeeLeave).filter(EmployeeLeave.id == uuid_obj).first()
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid leave ID format.")

    def get_leave_requests_by_employee(self, employee_id: str) -> List[EmployeeLeave]:
        try:
            uuid_obj = uuid.UUID(employee_id)
            return self.db.query(EmployeeLeave).filter(EmployeeLeave.employee_id == uuid_obj).all()
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid employee ID format.")

    def get_leave_requests_by_status(self, employee_id: str, status: str) -> List[EmployeeLeave]:
        try:
            uuid_obj = uuid.UUID(employee_id)
            return self.db.query(EmployeeLeave).filter(
                and_(
                    EmployeeLeave.employee_id == uuid_obj,
                    EmployeeLeave.status == status
                )
            ).all()
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid employee ID format.")

    def update_leave_request(self, leave_id: str, update_data: EmployeeLeaveDBSchema) -> Optional[EmployeeLeave]:
        leave = self.get_leave_request_by_id(leave_id)
        if not leave:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Leave request not found.")
        
        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(leave, field, value)
        
        try:
            self.db.commit()
            self.db.refresh(leave)
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Leave request update failed due to integrity error.")
        return leave

    def delete_leave_request(self, leave_id: str) -> bool:
        leave = self.get_leave_request_by_id(leave_id)
        if not leave:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Leave request not found.")
        leave.is_deleted=True
        self.db.commit()
        return True

    # ====================== SALARY LEDGER OPERATIONS ======================

    def create_salary_ledger_entry(self, salary_data: EmployeeSalaryLedgerDBSchema) -> EmployeeSalaryLedger:
        ledger_entry = EmployeeSalaryLedger(**salary_data.dict())
        self.db.add(ledger_entry)
        try:
            self.db.commit()
            self.db.refresh(ledger_entry)
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Salary ledger entry creation failed.")
        return ledger_entry

    def get_salary_ledger_by_id(self, ledger_id: str) -> Optional[EmployeeSalaryLedger]:
        try:
            uuid_obj = uuid.UUID(ledger_id)
            return self.db.query(EmployeeSalaryLedger).filter(EmployeeSalaryLedger.id == uuid_obj).first()
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid ledger ID format.")

    def get_salary_ledger_by_employee(self, employee_id: str) -> List[EmployeeSalaryLedger]:
        try:
            uuid_obj = uuid.UUID(employee_id)
            return self.db.query(EmployeeSalaryLedger).filter(EmployeeSalaryLedger.employee_id == uuid_obj).all()
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid employee ID format.")

    def update_salary_ledger_entry(self, ledger_id: str, update_data: EmployeeSalaryLedgerDBSchema) -> Optional[EmployeeSalaryLedger]:
        ledger_entry = self.get_salary_ledger_by_id(ledger_id)
        if not ledger_entry:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Salary ledger entry not found.")
        
        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(ledger_entry, field, value)
        
        try:
            self.db.commit()
            self.db.refresh(ledger_entry)
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Salary ledger entry update failed due to integrity error.")
        return ledger_entry

    def delete_salary_ledger_entry(self, ledger_id: str) -> bool:
        ledger_entry = self.get_salary_ledger_by_id(ledger_id)
        if not ledger_entry:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Salary ledger entry not found.")
        
        ledger_entry.is_deleted=True
        self.db.commit()
        return True

    # ====================== SEARCH AND FILTER OPERATIONS ======================

    def search_employees_by_name(self, name: str) -> List[EmployeeProfile]:
        return self.db.query(EmployeeProfile).filter(
            or_(
                EmployeeProfile.first_name.ilike(f"%{name}%"),
                EmployeeProfile.last_name.ilike(f"%{name}%"),
                EmployeeProfile.middle_name.ilike(f"%{name}%")
            )
        ).all()

    def get_employees_by_department(self, department: Department) -> List[EmployeeProfile]:
        return self.db.query(EmployeeProfile).filter(EmployeeProfile.department == department).all()

    def get_employees_by_status(self, status: EmployeeStatus) -> List[EmployeeProfile]:
        return self.db.query(EmployeeProfile).filter(EmployeeProfile.status == status).all()

    def get_employees_by_hire_date_range(self, start_date: datetime, end_date: datetime) -> List[EmployeeProfile]:
        return self.db.query(EmployeeProfile).filter(
            and_(
                EmployeeProfile.hire_date >= start_date,
                EmployeeProfile.hire_date <= end_date
            )
        ).all()

    def get_employees_by_salary_range(self, min_salary: float, max_salary: float) -> List[EmployeeProfile]:
        return self.db.query(EmployeeProfile).filter(
            and_(
                EmployeeProfile.salary >= min_salary,
                EmployeeProfile.salary <= max_salary
            )
        ).all()

    def get_employee_with_relationships(self, employee_id: str) -> Optional[EmployeeProfile]:
        try:
            uuid_obj = uuid.UUID(employee_id)
            return self.db.query(EmployeeProfile).filter(EmployeeProfile.id == uuid_obj).first()
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid employee ID format.")