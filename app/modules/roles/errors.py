from app.core.exceptions import ErrorFactory

NotFoundError = ErrorFactory.not_found("Role", error_code="RESOURCE_NOT_FOUND")