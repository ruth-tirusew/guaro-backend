import uuid
from datetime import datetime
from typing import List, Optional

from app.adapters.employee.interface import IEmployeeRepository
from app.adapters.employee.schema import (
    EmployeeProfileDBSchema,
    EmployeeDocumentDBSchema,
    EmployeePerformanceReviewDBSchema,
    EmployeeLeaveDBSchema,
    EmployeeSalaryLedgerDBSchema
)
from app.modules.employees.schemas import (
    EmployeeCreate, EmployeeUpdate, EmployeeRead, EmployeeList,
    EmployeeDocumentCreate, EmployeeDocumentUpdate, EmployeeDocumentRead, EmployeeDocumentList,
    EmployeePerformanceReviewCreate, EmployeePerformanceReviewUpdate, EmployeePerformanceReviewRead, EmployeePerformanceReviewList,
    EmployeeLeaveCreate, EmployeeLeaveUpdate, EmployeeLeaveRead, EmployeeLeaveList,
    EmployeeSalaryLedgerCreate, EmployeeSalaryLedgerUpdate, EmployeeSalaryLedgerRead, EmployeeSalaryLedgerList,
    EmployeeDetailResponse
)


class EmployeeService:
    def __init__(self, employee_repository: IEmployeeRepository):
        self.repository = employee_repository

    def create_employee(self, employee_data: EmployeeCreate) -> EmployeeRead:
        """Create a new employee profile"""
        existing_employee = self.repository.get_employee_by_employee_id(employee_data.employee_id)
        if existing_employee:
            raise ValueError("An employee with this employee ID already exists")

        if employee_data.email:
            existing_by_email = self.repository.get_employee_by_email(employee_data.email)
            if existing_by_email:
                raise ValueError("An employee with this email already exists")

        if employee_data.phone_number:
            existing_by_phone = self.repository.get_employee_by_phone(employee_data.phone_number)
            if existing_by_phone:
                raise ValueError("An employee with this phone number already exists")
        db_schema = EmployeeProfileDBSchema(**employee_data.dict())
        employee = self.repository.create_employee_profile(db_schema)
        
        return EmployeeRead.model_validate(employee)

    def get_employee(self, employee_id: str) -> Optional[EmployeeRead]:
        employee = self.repository.get_employee_by_id(employee_id)
        return EmployeeRead.model_validate(employee) if employee else None

    def get_employee_by_employee_id(self, employee_id: str) -> Optional[EmployeeRead]:
        employee = self.repository.get_employee_by_employee_id(employee_id)
        return EmployeeRead.model_validate(employee) if employee else None

    def get_employee_by_email(self, email: str) -> Optional[EmployeeRead]:
        employee = self.repository.get_employee_by_email(email)
        return EmployeeRead.model_validate(employee) if employee else None

    def get_employee_by_phone(self, phone_number: str) -> Optional[EmployeeRead]:
        employee = self.repository.get_employee_by_phone(phone_number)
        return EmployeeRead.model_validate(employee) if employee else None

    def list_employees(self) -> EmployeeList:
        employees = self.repository.get_all_employees()
        return EmployeeList(
            employees=[EmployeeRead.model_validate(employee) for employee in employees]
        )

    def update_employee(self, employee_id: str, update_data: EmployeeUpdate) -> Optional[EmployeeRead]:
        # Check for conflicts if email is being updated
        if update_data.email:
            existing_employee = self.repository.get_employee_by_email(update_data.email)
            if existing_employee and str(existing_employee.id) != employee_id:
                raise ValueError("An employee with this email already exists")

        # Check for conflicts if phone is being updated
        if update_data.phone_number:
            existing_employee = self.repository.get_employee_by_phone(update_data.phone_number)
            if existing_employee and str(existing_employee.id) != employee_id:
                raise ValueError("An employee with this phone number already exists")

        if update_data.employee_id:
            existing_employee = self.repository.get_employee_by_employee_id(update_data.employee_id)
            if existing_employee and str(existing_employee.id) != employee_id:
                raise ValueError("An employee with this employee ID already exists")

        db_schema = EmployeeProfileDBSchema(**update_data.dict(exclude_unset=True))
        employee = self.repository.update_employee_profile(employee_id, db_schema)
        return EmployeeRead.model_validate(employee) if employee else None

    def delete_employee(self, employee_id: str) -> bool:
        """Delete an employee profile"""
        return self.repository.delete_employee_profile(employee_id)

    def activate_employee(self, employee_id: str) -> bool:
        """Activate an employee account"""
        return self.repository.activate_employee(employee_id)

    def deactivate_employee(self, employee_id: str) -> bool:
        """Deactivate an employee account"""
        return self.repository.deactivate_employee(employee_id)

    def create_employee_document(self, document_data: EmployeeDocumentCreate) -> EmployeeDocumentRead:
        """Create a new employee document"""
        db_schema = EmployeeDocumentDBSchema(**document_data.dict())
        document = self.repository.create_employee_document(db_schema)
        return EmployeeDocumentRead.model_validate(document)

    def get_employee_document(self, document_id: str) -> Optional[EmployeeDocumentRead]:
        """Get an employee document by ID"""
        document = self.repository.get_employee_document_by_id(document_id)
        return EmployeeDocumentRead.model_validate(document) if document else None

    def get_employee_documents(self, employee_id: str) -> EmployeeDocumentList:
        """Get all documents for an employee"""
        documents = self.repository.get_employee_documents_by_employee(employee_id)
        return EmployeeDocumentList(
            documents=[EmployeeDocumentRead.model_validate(doc) for doc in documents]
        )

    def get_employee_documents_by_type(self, employee_id: str, document_type: str) -> EmployeeDocumentList:
        """Get documents of a specific type for an employee"""
        documents = self.repository.get_employee_documents_by_type(employee_id, document_type)
        return EmployeeDocumentList(
            documents=[EmployeeDocumentRead.model_validate(doc) for doc in documents]
        )

    def update_employee_document(self, document_id: str, update_data: EmployeeDocumentUpdate) -> Optional[EmployeeDocumentRead]:
        """Update an employee document"""
        db_schema = EmployeeDocumentDBSchema(**update_data.dict(exclude_unset=True))
        document = self.repository.update_employee_document(document_id, db_schema)
        return EmployeeDocumentRead.model_validate(document) if document else None

    def delete_employee_document(self, document_id: str) -> bool:
        """Delete an employee document"""
        return self.repository.delete_employee_document(document_id)

    # ====================== PERFORMANCE REVIEW OPERATIONS ======================

    def create_performance_review(self, review_data: EmployeePerformanceReviewCreate) -> EmployeePerformanceReviewRead:
        """Create a new performance review"""
        db_schema = EmployeePerformanceReviewDBSchema(**review_data.dict())
        review = self.repository.create_performance_review(db_schema)
        return EmployeePerformanceReviewRead.model_validate(review)

    def get_performance_review(self, review_id: str) -> Optional[EmployeePerformanceReviewRead]:
        """Get a performance review by ID"""
        review = self.repository.get_performance_review_by_id(review_id)
        return EmployeePerformanceReviewRead.model_validate(review) if review else None

    def get_employee_performance_reviews(self, employee_id: str) -> EmployeePerformanceReviewList:
        """Get all performance reviews for an employee"""
        reviews = self.repository.get_performance_reviews_by_employee(employee_id)
        return EmployeePerformanceReviewList(
            reviews=[EmployeePerformanceReviewRead.model_validate(review) for review in reviews]
        )

    def update_performance_review(self, review_id: str, update_data: EmployeePerformanceReviewUpdate) -> Optional[EmployeePerformanceReviewRead]:
        """Update a performance review"""
        db_schema = EmployeePerformanceReviewDBSchema(**update_data.dict(exclude_unset=True))
        review = self.repository.update_performance_review(review_id, db_schema)
        return EmployeePerformanceReviewRead.model_validate(review) if review else None

    def delete_performance_review(self, review_id: str) -> bool:
        """Delete a performance review"""
        return self.repository.delete_performance_review(review_id)

    # ====================== LEAVE OPERATIONS ======================

    def create_leave_request(self, leave_data: EmployeeLeaveCreate) -> EmployeeLeaveRead:
        db_schema = EmployeeLeaveDBSchema(**leave_data.dict())
        leave = self.repository.create_leave_request(db_schema)
        return EmployeeLeaveRead.model_validate(leave)

    def get_leave_request(self, leave_id: str) -> Optional[EmployeeLeaveRead]:
        leave = self.repository.get_leave_request_by_id(leave_id)
        return EmployeeLeaveRead.model_validate(leave) if leave else None

    def get_employee_leave_requests(self, employee_id: str) -> EmployeeLeaveList:
        leaves = self.repository.get_leave_requests_by_employee(employee_id)
        return EmployeeLeaveList(
            leaves=[EmployeeLeaveRead.model_validate(leave) for leave in leaves]
        )

    def get_employee_leave_requests_by_status(self, employee_id: str, status: str) -> EmployeeLeaveList:
        leaves = self.repository.get_leave_requests_by_status(employee_id, status)
        return EmployeeLeaveList(
            leaves=[EmployeeLeaveRead.model_validate(leave) for leave in leaves]
        )

    def update_leave_request(self, leave_id: str, update_data: EmployeeLeaveUpdate) -> Optional[EmployeeLeaveRead]:
        db_schema = EmployeeLeaveDBSchema(**update_data.dict(exclude_unset=True))
        leave = self.repository.update_leave_request(leave_id, db_schema)
        return EmployeeLeaveRead.model_validate(leave) if leave else None

    def delete_leave_request(self, leave_id: str) -> bool:
        return self.repository.delete_leave_request(leave_id)


    def create_salary_ledger_entry(self, salary_data: EmployeeSalaryLedgerCreate) -> EmployeeSalaryLedgerRead:
        db_schema = EmployeeSalaryLedgerDBSchema(**salary_data.dict())
        ledger_entry = self.repository.create_salary_ledger_entry(db_schema)
        return EmployeeSalaryLedgerRead.model_validate(ledger_entry)

    def get_salary_ledger_entry(self, ledger_id: str) -> Optional[EmployeeSalaryLedgerRead]:
        ledger_entry = self.repository.get_salary_ledger_by_id(ledger_id)
        return EmployeeSalaryLedgerRead.model_validate(ledger_entry) if ledger_entry else None

    def get_employee_salary_ledger(self, employee_id: str) -> EmployeeSalaryLedgerList:
        ledger_entries = self.repository.get_salary_ledger_by_employee(employee_id)
        return EmployeeSalaryLedgerList(
            salary_ledger=[EmployeeSalaryLedgerRead.model_validate(entry) for entry in ledger_entries]
        )

    def update_salary_ledger_entry(self, ledger_id: str, update_data: EmployeeSalaryLedgerUpdate) -> Optional[EmployeeSalaryLedgerRead]:
        db_schema = EmployeeSalaryLedgerDBSchema(**update_data.dict(exclude_unset=True))
        ledger_entry = self.repository.update_salary_ledger_entry(ledger_id, db_schema)
        return EmployeeSalaryLedgerRead.model_validate(ledger_entry) if ledger_entry else None

    def delete_salary_ledger_entry(self, ledger_id: str) -> bool:
        return self.repository.delete_salary_ledger_entry(ledger_id)

    # ====================== SEARCH AND FILTER OPERATIONS ======================

    def search_employees_by_name(self, name: str) -> EmployeeList:
        employees = self.repository.search_employees_by_name(name)
        return EmployeeList(
            employees=[EmployeeRead.model_validate(employee) for employee in employees]
        )

    def get_employees_by_department(self, department: str) -> EmployeeList:
        from app.adapters.employee.models import Department
        dept_enum = Department(department)
        employees = self.repository.get_employees_by_department(dept_enum)
        return EmployeeList(
            employees=[EmployeeRead.model_validate(employee) for employee in employees]
        )

    def get_employees_by_status(self, status: str) -> EmployeeList:
        from app.adapters.employee.models import EmployeeStatus
        status_enum = EmployeeStatus(status)
        employees = self.repository.get_employees_by_status(status_enum)
        return EmployeeList(
            employees=[EmployeeRead.model_validate(employee) for employee in employees]
        )

    def get_employees_by_hire_date_range(self, start_date: datetime, end_date: datetime) -> EmployeeList:
        employees = self.repository.get_employees_by_hire_date_range(start_date, end_date)
        return EmployeeList(
            employees=[EmployeeRead.model_validate(employee) for employee in employees]
        )

    def get_employees_by_salary_range(self, min_salary: float, max_salary: float) -> EmployeeList:
        employees = self.repository.get_employees_by_salary_range(min_salary, max_salary)
        return EmployeeList(
            employees=[EmployeeRead.model_validate(employee) for employee in employees]
        )


    def get_employee_with_relationships(self, employee_id: str) -> Optional[EmployeeDetailResponse]:
        employee = self.repository.get_employee_with_relationships(employee_id)
        if not employee:
            return None

        documents = self.get_employee_documents(employee_id)
        performance_reviews = self.get_employee_performance_reviews(employee_id)
        leave_records = self.get_employee_leave_requests(employee_id)
        salary_ledger = self.get_employee_salary_ledger(employee_id)

        return EmployeeDetailResponse(
            employee=EmployeeRead.model_validate(employee),
            documents=documents,
            performance_reviews=performance_reviews,
            leave_records=leave_records,
            salary_ledger=salary_ledger
        )
