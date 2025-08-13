from abc import ABC, abstractmethod
from typing import Optional, List
from datetime import datetime

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


class IEmployeeRepository(ABC):
    # ====================== EMPLOYEE PROFILE OPERATIONS ======================
    
    @abstractmethod
    def create_employee_profile(self, employee_data: EmployeeProfileDBSchema) -> EmployeeProfile:
        """
        Create a new employee profile record.
        
        Args:
            employee_data: Employee profile data
            
        Returns:
            EmployeeProfile: The created employee profile instance
            
        Raises:
            ValidationError: If employee data is invalid
            DatabaseError: If creation fails
        """
        pass

    @abstractmethod
    def get_employee_by_id(self, employee_id: str) -> Optional[EmployeeProfile]:
        """
        Retrieve an employee by their unique identifier.
        
        Args:
            employee_id: Unique identifier for the employee
            
        Returns:
            Optional[EmployeeProfile]: The employee instance if found, None otherwise
        """
        pass

    @abstractmethod
    def get_employee_by_employee_id(self, employee_id: str) -> Optional[EmployeeProfile]:
        """
        Retrieve an employee by their employee ID.
        
        Args:
            employee_id: Employee ID string
            
        Returns:
            Optional[EmployeeProfile]: The employee instance if found, None otherwise
        """
        pass

    @abstractmethod
    def get_employee_by_email(self, email: str) -> Optional[EmployeeProfile]:
        """
        Retrieve an employee by their email address.
        
        Args:
            email: Email address of the employee
            
        Returns:
            Optional[EmployeeProfile]: The employee instance if found, None otherwise
        """
        pass

    @abstractmethod
    def get_employee_by_phone(self, phone_number: str) -> Optional[EmployeeProfile]:
        """
        Retrieve an employee by their phone number.
        
        Args:
            phone_number: Phone number of the employee
            
        Returns:
            Optional[EmployeeProfile]: The employee instance if found, None otherwise
        """
        pass

    @abstractmethod
    def get_all_employees(self) -> List[EmployeeProfile]:
        """
        Retrieve all employees in the system.
        
        Returns:
            List[EmployeeProfile]: List of all employee instances
        """
        pass

    @abstractmethod
    def update_employee_profile(self, employee_id: str, update_data: EmployeeProfileDBSchema) -> Optional[EmployeeProfile]:
        """
        Update existing employee profile information.
        
        Args:
            employee_id: Unique identifier for the employee
            update_data: Dictionary containing updated fields
            
        Returns:
            Optional[EmployeeProfile]: Updated employee instance if successful, None otherwise
        """
        pass

    @abstractmethod
    def delete_employee_profile(self, employee_id: str) -> bool:
        """
        Permanently delete an employee profile record.
        
        Args:
            employee_id: Unique identifier for the employee
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        pass

    @abstractmethod
    def activate_employee(self, employee_id: str) -> bool:
        """
        Activate an employee account.
        
        Args:
            employee_id: Unique identifier for the employee
            
        Returns:
            bool: True if activation was successful, False otherwise
        """
        pass

    @abstractmethod
    def deactivate_employee(self, employee_id: str) -> bool:
        """
        Deactivate an employee account.
        
        Args:
            employee_id: Unique identifier for the employee
            
        Returns:
            bool: True if deactivation was successful, False otherwise
        """
        pass

    # ====================== EMPLOYEE DOCUMENT OPERATIONS ======================

    @abstractmethod
    def create_employee_document(self, document_data: EmployeeDocumentDBSchema) -> EmployeeDocument:
        """
        Create a new employee document record.
        
        Args:
            document_data: Document data
            
        Returns:
            EmployeeDocument: The created document instance
        """
        pass

    @abstractmethod
    def get_employee_document_by_id(self, document_id: str) -> Optional[EmployeeDocument]:
        """
        Retrieve an employee document by its unique identifier.
        
        Args:
            document_id: Unique identifier for the document
            
        Returns:
            Optional[EmployeeDocument]: The document instance if found, None otherwise
        """
        pass

    @abstractmethod
    def get_employee_documents_by_employee(self, employee_id: str) -> List[EmployeeDocument]:
        """
        Retrieve all documents for a specific employee.
        
        Args:
            employee_id: Unique identifier for the employee
            
        Returns:
            List[EmployeeDocument]: List of employee documents
        """
        pass

    @abstractmethod
    def get_employee_documents_by_type(self, employee_id: str, document_type: str) -> List[EmployeeDocument]:
        """
        Retrieve documents of a specific type for an employee.
        
        Args:
            employee_id: Unique identifier for the employee
            document_type: Type of document to retrieve
            
        Returns:
            List[EmployeeDocument]: List of documents of specified type
        """
        pass

    @abstractmethod
    def update_employee_document(self, document_id: str, update_data: EmployeeDocumentDBSchema) -> Optional[EmployeeDocument]:
        """
        Update existing employee document information.
        
        Args:
            document_id: Unique identifier for the document
            update_data: Dictionary containing updated fields
            
        Returns:
            Optional[EmployeeDocument]: Updated document instance if successful, None otherwise
        """
        pass

    @abstractmethod
    def delete_employee_document(self, document_id: str) -> bool:
        """
        Delete an employee document record.
        
        Args:
            document_id: Unique identifier for the document
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        pass

    # ====================== PERFORMANCE REVIEW OPERATIONS ======================

    @abstractmethod
    def create_performance_review(self, review_data: EmployeePerformanceReviewDBSchema) -> EmployeePerformanceReview:
        """
        Create a new performance review record.
        
        Args:
            review_data: Performance review data
            
        Returns:
            EmployeePerformanceReview: The created review instance
        """
        pass

    @abstractmethod
    def get_performance_review_by_id(self, review_id: str) -> Optional[EmployeePerformanceReview]:
        """
        Retrieve a performance review by its unique identifier.
        
        Args:
            review_id: Unique identifier for the review
            
        Returns:
            Optional[EmployeePerformanceReview]: The review instance if found, None otherwise
        """
        pass

    @abstractmethod
    def get_performance_reviews_by_employee(self, employee_id: str) -> List[EmployeePerformanceReview]:
        """
        Retrieve all performance reviews for a specific employee.
        
        Args:
            employee_id: Unique identifier for the employee
            
        Returns:
            List[EmployeePerformanceReview]: List of performance reviews
        """
        pass

    @abstractmethod
    def update_performance_review(self, review_id: str, update_data: EmployeePerformanceReviewDBSchema) -> Optional[EmployeePerformanceReview]:
        """
        Update existing performance review information.
        
        Args:
            review_id: Unique identifier for the review
            update_data: Dictionary containing updated fields
            
        Returns:
            Optional[EmployeePerformanceReview]: Updated review instance if successful, None otherwise
        """
        pass

    @abstractmethod
    def delete_performance_review(self, review_id: str) -> bool:
        """
        Delete a performance review record.
        
        Args:
            review_id: Unique identifier for the review
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        pass

    # ====================== LEAVE OPERATIONS ======================

    @abstractmethod
    def create_leave_request(self, leave_data: EmployeeLeaveDBSchema) -> EmployeeLeave:
        """
        Create a new leave request record.
        
        Args:
            leave_data: Leave request data
            
        Returns:
            EmployeeLeave: The created leave request instance
        """
        pass

    @abstractmethod
    def get_leave_request_by_id(self, leave_id: str) -> Optional[EmployeeLeave]:
        """
        Retrieve a leave request by its unique identifier.
        
        Args:
            leave_id: Unique identifier for the leave request
            
        Returns:
            Optional[EmployeeLeave]: The leave request instance if found, None otherwise
        """
        pass

    @abstractmethod
    def get_leave_requests_by_employee(self, employee_id: str) -> List[EmployeeLeave]:
        """
        Retrieve all leave requests for a specific employee.
        
        Args:
            employee_id: Unique identifier for the employee
            
        Returns:
            List[EmployeeLeave]: List of leave requests
        """
        pass

    @abstractmethod
    def get_leave_requests_by_status(self, employee_id: str, status: str) -> List[EmployeeLeave]:
        """
        Retrieve leave requests by status for an employee.
        
        Args:
            employee_id: Unique identifier for the employee
            status: Status of leave requests to retrieve
            
        Returns:
            List[EmployeeLeave]: List of leave requests with specified status
        """
        pass

    @abstractmethod
    def update_leave_request(self, leave_id: str, update_data: EmployeeLeaveDBSchema) -> Optional[EmployeeLeave]:
        """
        Update existing leave request information.
        
        Args:
            leave_id: Unique identifier for the leave request
            update_data: Dictionary containing updated fields
            
        Returns:
            Optional[EmployeeLeave]: Updated leave request instance if successful, None otherwise
        """
        pass

    @abstractmethod
    def delete_leave_request(self, leave_id: str) -> bool:
        """
        Delete a leave request record.
        
        Args:
            leave_id: Unique identifier for the leave request
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        pass

    # ====================== SALARY LEDGER OPERATIONS ======================

    @abstractmethod
    def create_salary_ledger_entry(self, salary_data: EmployeeSalaryLedgerDBSchema) -> EmployeeSalaryLedger:
        """
        Create a new salary ledger entry.
        
        Args:
            salary_data: Salary ledger data
            
        Returns:
            EmployeeSalaryLedger: The created salary ledger instance
        """
        pass

    @abstractmethod
    def get_salary_ledger_by_id(self, ledger_id: str) -> Optional[EmployeeSalaryLedger]:
        """
        Retrieve a salary ledger entry by its unique identifier.
        
        Args:
            ledger_id: Unique identifier for the salary ledger entry
            
        Returns:
            Optional[EmployeeSalaryLedger]: The salary ledger instance if found, None otherwise
        """
        pass

    @abstractmethod
    def get_salary_ledger_by_employee(self, employee_id: str) -> List[EmployeeSalaryLedger]:
        """
        Retrieve all salary ledger entries for a specific employee.
        
        Args:
            employee_id: Unique identifier for the employee
            
        Returns:
            List[EmployeeSalaryLedger]: List of salary ledger entries
        """
        pass

    @abstractmethod
    def update_salary_ledger_entry(self, ledger_id: str, update_data: EmployeeSalaryLedgerDBSchema) -> Optional[EmployeeSalaryLedger]:
        """
        Update existing salary ledger entry information.
        
        Args:
            ledger_id: Unique identifier for the salary ledger entry
            update_data: Dictionary containing updated fields
            
        Returns:
            Optional[EmployeeSalaryLedger]: Updated salary ledger instance if successful, None otherwise
        """
        pass

    @abstractmethod
    def delete_salary_ledger_entry(self, ledger_id: str) -> bool:
        """
        Delete a salary ledger entry record.
        
        Args:
            ledger_id: Unique identifier for the salary ledger entry
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        pass

    # ====================== SEARCH AND FILTER OPERATIONS ======================

    @abstractmethod
    def search_employees_by_name(self, name: str) -> List[EmployeeProfile]:
        """
        Search employees by name (first name, last name, or middle name).
        
        Args:
            name: Name to search for
            
        Returns:
            List[EmployeeProfile]: List of matching employees
        """
        pass

    @abstractmethod
    def get_employees_by_department(self, department: Department) -> List[EmployeeProfile]:
        """
        Get all employees in a specific department.
        
        Args:
            department: Department to filter by
            
        Returns:
            List[EmployeeProfile]: List of employees in the department
        """
        pass

    @abstractmethod
    def get_employees_by_status(self, status: EmployeeStatus) -> List[EmployeeProfile]:
        """
        Get all employees with a specific status.
        
        Args:
            status: Employee status to filter by
            
        Returns:
            List[EmployeeProfile]: List of employees with the specified status
        """
        pass

    @abstractmethod
    def get_employees_by_hire_date_range(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[EmployeeProfile]:
        """
        Get employees hired within a specific date range.
        
        Args:
            start_date: Start date for the range
            end_date: End date for the range
            
        Returns:
            List[EmployeeProfile]: List of employees hired in the date range
        """
        pass

    @abstractmethod
    def get_employees_by_salary_range(
        self, 
        min_salary: float, 
        max_salary: float
    ) -> List[EmployeeProfile]:
        """
        Get employees within a specific salary range.
        
        Args:
            min_salary: Minimum salary threshold
            max_salary: Maximum salary threshold
            
        Returns:
            List[EmployeeProfile]: List of employees in the salary range
        """
        pass

    @abstractmethod
    def get_employee_with_relationships(self, employee_id: str) -> Optional[EmployeeProfile]:
        """
        Get employee with all related data (documents, reviews, leave, salary ledger).
        
        Args:
            employee_id: Unique identifier for the employee
            
        Returns:
            Optional[EmployeeProfile]: Employee with all relationships loaded
        """
        pass
