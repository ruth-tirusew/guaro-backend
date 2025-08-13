from datetime import datetime
from fastapi import APIRouter, HTTPException, status, Query, Depends
from typing import Optional

from app.modules.employees.schemas import (
    EmployeeCreate, EmployeeUpdate, EmployeeRead, EmployeeList,
    EmployeeDocumentCreate, EmployeeDocumentUpdate, EmployeeDocumentRead, EmployeeDocumentList,
    EmployeePerformanceReviewCreate, EmployeePerformanceReviewUpdate, EmployeePerformanceReviewRead, EmployeePerformanceReviewList,
    EmployeeLeaveCreate, EmployeeLeaveUpdate, EmployeeLeaveRead, EmployeeLeaveList,
    EmployeeSalaryLedgerCreate, EmployeeSalaryLedgerUpdate, EmployeeSalaryLedgerRead, EmployeeSalaryLedgerList,
    EmployeeDetailResponse
)
from app.dependencies import EmployeeServiceDep
from app.modules.employees.service import EmployeeService

router = APIRouter(prefix="/employees", tags=["Employees"])

# ====================== EMPLOYEE PROFILE ENDPOINTS ======================

@router.post("/", response_model=EmployeeRead, status_code=status.HTTP_201_CREATED)
def create_employee(employee: EmployeeCreate, employee_service: EmployeeServiceDep):
    """Create a new employee profile"""
    try:
        return employee_service.create_employee(employee)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/{employee_id}", response_model=EmployeeRead)
def get_employee(employee_id: str, employee_service: EmployeeServiceDep):
    """Get an employee by ID"""
    employee = employee_service.get_employee(employee_id)
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    return employee

@router.get("/by-employee-id/{employee_id}", response_model=EmployeeRead)
def get_employee_by_employee_id(employee_id: str, employee_service: EmployeeServiceDep):
    """Get an employee by employee ID"""
    employee = employee_service.get_employee_by_employee_id(employee_id)
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    return employee

@router.get("/by-email/{email}", response_model=EmployeeRead)
def get_employee_by_email(email: str, employee_service: EmployeeServiceDep):
    """Get an employee by email"""
    employee = employee_service.get_employee_by_email(email)
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    return employee

@router.get("/by-phone/{phone_number}", response_model=EmployeeRead)
def get_employee_by_phone(phone_number: str, employee_service: EmployeeServiceDep):
    """Get an employee by phone number"""
    employee = employee_service.get_employee_by_phone(phone_number)
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    return employee

@router.get("/", response_model=EmployeeList)
def list_employees(employee_service: EmployeeServiceDep):
    """Get all employees"""
    return employee_service.list_employees()

@router.put("/{employee_id}", response_model=EmployeeRead)
def update_employee(employee_id: str, employee_update: EmployeeUpdate, employee_service: EmployeeServiceDep):
    """Update an employee profile"""
    try:
        employee = employee_service.update_employee(employee_id, employee_update)
        if not employee:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
        return employee
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee(employee_id: str, employee_service: EmployeeServiceDep):
    """Delete an employee profile"""
    employee_service.delete_employee(employee_id)
    return None

@router.post("/{employee_id}/activate", status_code=status.HTTP_200_OK)
def activate_employee(employee_id: str, employee_service: EmployeeServiceDep):
    """Activate an employee account"""
    try:
        employee_service.activate_employee(employee_id)
        return {"message": "Employee activated successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/{employee_id}/deactivate", status_code=status.HTTP_200_OK)
def deactivate_employee(employee_id: str, employee_service: EmployeeServiceDep):
    """Deactivate an employee account"""
    try:
        employee_service.deactivate_employee(employee_id)
        return {"message": "Employee deactivated successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/{employee_id}/detail", response_model=EmployeeDetailResponse)
def get_employee_with_relationships(employee_id: str, employee_service: EmployeeServiceDep):
    """Get employee with all related data"""
    employee_detail = employee_service.get_employee_with_relationships(employee_id)
    if not employee_detail:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    return employee_detail

# ====================== SEARCH AND FILTER ENDPOINTS ======================

@router.get("/search/name/{name}", response_model=EmployeeList)
def search_employees_by_name(name: str, employee_service: EmployeeServiceDep):
    """Search employees by name"""
    return employee_service.search_employees_by_name(name)

@router.get("/filter/department/{department}", response_model=EmployeeList)
def get_employees_by_department(department: str, employee_service: EmployeeServiceDep):
    """Get employees by department"""
    return employee_service.get_employees_by_department(department)

@router.get("/filter/status/{status}", response_model=EmployeeList)
def get_employees_by_status(status: str, employee_service: EmployeeServiceDep):
    """Get employees by status"""
    return employee_service.get_employees_by_status(status)

@router.get("/filter/hire-date-range", response_model=EmployeeList)
def get_employees_by_hire_date_range(
    employee_service: EmployeeServiceDep,
    start_date: datetime = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: datetime = Query(..., description="End date (YYYY-MM-DD)"),
):
    """Get employees hired within a date range"""
    return employee_service.get_employees_by_hire_date_range(start_date, end_date)

@router.get("/filter/salary-range", response_model=EmployeeList)
def get_employees_by_salary_range(
    employee_service: EmployeeServiceDep,
    min_salary: float = Query(..., description="Minimum salary"),
    max_salary: float = Query(..., description="Maximum salary"),
):
    """Get employees within a salary range"""
    return employee_service.get_employees_by_salary_range(min_salary, max_salary)

# ====================== EMPLOYEE DOCUMENT ENDPOINTS ======================

@router.post("/documents", response_model=EmployeeDocumentRead, status_code=status.HTTP_201_CREATED)
def create_employee_document(document: EmployeeDocumentCreate, employee_service: EmployeeServiceDep):
    """Create a new employee document"""
    try:
        return employee_service.create_employee_document(document)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/documents/{document_id}", response_model=EmployeeDocumentRead)
def get_employee_document(document_id: str, employee_service: EmployeeServiceDep):
    """Get an employee document by ID"""
    document = employee_service.get_employee_document(document_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return document

@router.get("/{employee_id}/documents", response_model=EmployeeDocumentList)
def get_employee_documents(employee_id: str, employee_service: EmployeeServiceDep):
    """Get all documents for an employee"""
    return employee_service.get_employee_documents(employee_id)

@router.get("/{employee_id}/documents/type/{document_type}", response_model=EmployeeDocumentList)
def get_employee_documents_by_type(employee_id: str, document_type: str, employee_service: EmployeeServiceDep):
    """Get documents of a specific type for an employee"""
    return employee_service.get_employee_documents_by_type(employee_id, document_type)

@router.put("/documents/{document_id}", response_model=EmployeeDocumentRead)
def update_employee_document(document_id: str, document_update: EmployeeDocumentUpdate, employee_service: EmployeeServiceDep):
    """Update an employee document"""
    try:
        document = employee_service.update_employee_document(document_id, document_update)
        if not document:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
        return document
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee_document(document_id: str, employee_service: EmployeeServiceDep):
    """Delete an employee document"""
    employee_service.delete_employee_document(document_id)
    return None

# ====================== PERFORMANCE REVIEW ENDPOINTS ======================

@router.post("/performance-reviews", response_model=EmployeePerformanceReviewRead, status_code=status.HTTP_201_CREATED)
def create_performance_review(review: EmployeePerformanceReviewCreate, employee_service: EmployeeServiceDep):
    """Create a new performance review"""
    try:
        return employee_service.create_performance_review(review)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/performance-reviews/{review_id}", response_model=EmployeePerformanceReviewRead)
def get_performance_review(review_id: str, employee_service: EmployeeServiceDep):
    """Get a performance review by ID"""
    review = employee_service.get_performance_review(review_id)
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Performance review not found")
    return review

@router.get("/{employee_id}/performance-reviews", response_model=EmployeePerformanceReviewList)
def get_employee_performance_reviews(employee_id: str, employee_service: EmployeeServiceDep):
    """Get all performance reviews for an employee"""
    return employee_service.get_employee_performance_reviews(employee_id)

@router.put("/performance-reviews/{review_id}", response_model=EmployeePerformanceReviewRead)
def update_performance_review(review_id: str, review_update: EmployeePerformanceReviewUpdate, employee_service: EmployeeServiceDep):
    """Update a performance review"""
    try:
        review = employee_service.update_performance_review(review_id, review_update)
        if not review:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Performance review not found")
        return review
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/performance-reviews/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_performance_review(review_id: str, employee_service: EmployeeServiceDep):
    """Delete a performance review"""
    employee_service.delete_performance_review(review_id)
    return None

# ====================== LEAVE REQUEST ENDPOINTS ======================

@router.post("/leave-requests", response_model=EmployeeLeaveRead, status_code=status.HTTP_201_CREATED)
def create_leave_request(leave: EmployeeLeaveCreate, employee_service: EmployeeServiceDep):
    """Create a new leave request"""
    try:
        return employee_service.create_leave_request(leave)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/leave-requests/{leave_id}", response_model=EmployeeLeaveRead)
def get_leave_request(leave_id: str, employee_service: EmployeeServiceDep):
    """Get a leave request by ID"""
    leave = employee_service.get_leave_request(leave_id)
    if not leave:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Leave request not found")
    return leave

@router.get("/{employee_id}/leave-requests", response_model=EmployeeLeaveList)
def get_employee_leave_requests(employee_id: str, employee_service: EmployeeServiceDep):
    """Get all leave requests for an employee"""
    return employee_service.get_employee_leave_requests(employee_id)

@router.get("/{employee_id}/leave-requests/status/{status}", response_model=EmployeeLeaveList)
def get_employee_leave_requests_by_status(employee_id: str, status: str, employee_service: EmployeeServiceDep):
    """Get leave requests by status for an employee"""
    return employee_service.get_employee_leave_requests_by_status(employee_id, status)

@router.put("/leave-requests/{leave_id}", response_model=EmployeeLeaveRead)
def update_leave_request(leave_id: str, leave_update: EmployeeLeaveUpdate, employee_service: EmployeeServiceDep):
    """Update a leave request"""
    try:
        leave = employee_service.update_leave_request(leave_id, leave_update)
        if not leave:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Leave request not found")
        return leave
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/leave-requests/{leave_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_leave_request(leave_id: str, employee_service: EmployeeServiceDep):
    """Delete a leave request"""
    employee_service.delete_leave_request(leave_id)
    return None

# ====================== SALARY LEDGER ENDPOINTS ======================

@router.post("/salary-ledger", response_model=EmployeeSalaryLedgerRead, status_code=status.HTTP_201_CREATED)
def create_salary_ledger_entry(ledger_entry: EmployeeSalaryLedgerCreate, employee_service: EmployeeServiceDep):
    """Create a new salary ledger entry"""
    try:
        return employee_service.create_salary_ledger_entry(ledger_entry)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/salary-ledger/{ledger_id}", response_model=EmployeeSalaryLedgerRead)
def get_salary_ledger_entry(ledger_id: str, employee_service: EmployeeServiceDep):
    """Get a salary ledger entry by ID"""
    ledger_entry = employee_service.get_salary_ledger_entry(ledger_id)
    if not ledger_entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Salary ledger entry not found")
    return ledger_entry

@router.get("/{employee_id}/salary-ledger", response_model=EmployeeSalaryLedgerList)
def get_employee_salary_ledger(employee_id: str, employee_service: EmployeeServiceDep):
    """Get all salary ledger entries for an employee"""
    return employee_service.get_employee_salary_ledger(employee_id)

@router.put("/salary-ledger/{ledger_id}", response_model=EmployeeSalaryLedgerRead)
def update_salary_ledger_entry(ledger_id: str, ledger_update: EmployeeSalaryLedgerUpdate, employee_service: EmployeeServiceDep):
    """Update a salary ledger entry"""
    try:
        ledger_entry = employee_service.update_salary_ledger_entry(ledger_id, ledger_update)
        if not ledger_entry:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Salary ledger entry not found")
        return ledger_entry
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/salary-ledger/{ledger_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_salary_ledger_entry(ledger_id: str, employee_service: EmployeeServiceDep):
    """Delete a salary ledger entry"""
    employee_service.delete_salary_ledger_entry(ledger_id)
    return None
