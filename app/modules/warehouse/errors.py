from app.core.exceptions import ErrorFactory

NotFoundError = ErrorFactory.not_found("Warehouse", error_code="RESOURCE_NOT_FOUND")