from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import ValidationError
import logging
import traceback
from datetime import datetime, timezone

from app.config import settings, fastapi_config
from app.database import engine
from app.logging import logger
from app.core.exceptions import APIError, ErrorFactory

from app.modules.authentication.router import router as authentication_router
from app.modules.employees.router import router as employee_router
from app.modules.farmers.router import router as farmer_router
from app.modules.biodata.router import router as biodata_router
from app.modules.products.router import router as product_router
from app.modules.products.router import category_router
from app.modules.resources.router import router as resource_router
from app.modules.roles.router import router as role_router
from app.modules.warehouse.router import router as warehouse_router
from app.modules.users.router import router as user_router

from app.utils.middlewares.authorization import auth_middleware

app = FastAPI(**fastapi_config)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
    allow_credentials=True,
)

# Add authorization middleware
@app.middleware("http")
async def authorization_middleware(request: Request, call_next):
    """Authorization middleware for role-based access control"""
    return await auth_middleware.middleware(request, call_next)

prefix ="/api/v1"

app.include_router(authentication_router, prefix=prefix)
app.include_router(biodata_router, prefix=prefix)
app.include_router(employee_router, prefix=prefix)
app.include_router(farmer_router, prefix=prefix)
app.include_router(product_router, prefix=prefix)
app.include_router(category_router, prefix=prefix)
app.include_router(role_router, prefix=prefix)
app.include_router(resource_router, prefix=prefix)
app.include_router(user_router, prefix=prefix)
app.include_router(warehouse_router, prefix=prefix)


@app.exception_handler(APIError)
async def api_error_handler(request: Request, exc: APIError):
    """Handle custom API errors"""
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict()
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle FastAPI request validation errors (422)"""
    errors = []
    for error in exc.errors():
        field = '.'.join(str(loc) for loc in error['loc'])
        errors.append({
            "field": field,
            "message": error['msg'],
            "value": error.get('input')
        })

    api_error = APIError(
        status_code=422,
        detail="Request validation failed",
        user_message="Please check your input data and try again",
        error_code="VALIDATION_FAILED",
        context={
            "validation_errors": errors,
            "request_url": str(request.url),
            "request_method": request.method
        }
    )
    
    return JSONResponse(
        status_code=422,
        content=api_error.to_dict()
    )


@app.exception_handler(ValidationError)
async def pydantic_validation_handler(request: Request, exc: ValidationError):
    api_error = ErrorFactory.validation_error(
        field="request_body",
        user_message="Invalid data format provided",
        context={
            "pydantic_errors": exc.errors(),
            "request_url": str(request.url),
            "request_method": request.method
        }
    )
    
    return JSONResponse(
        status_code=422,
        content=api_error.to_dict()
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        api_error = ErrorFactory.not_found(
            resource="Endpoint",
            user_message="The requested endpoint was not found",
            context={
                "request_url": str(request.url),
                "request_method": request.method,
                "status_code": exc.status_code
            }
        )
    elif exc.status_code == 405:
        api_error = APIError(
            status_code=405,
            detail="Method not allowed",
            user_message=f"Method {request.method} is not allowed for this endpoint",
            error_code="METHOD_NOT_ALLOWED",
            context={
                "request_url": str(request.url),
                "request_method": request.method,
                "allowed_methods": getattr(exc, 'allowed_methods', [])
            }
        )
    else:
        logger.error(
            f"Error detail: {str(exc.detail)}"
        )
        api_error = APIError(
            status_code=exc.status_code,
            detail=str(exc.detail) if exc.status_code < 500 else "An error occurred processing your request",
            user_message=str(exc.detail) if exc.status_code < 500 else "An error occurred processing your request",
            error_code=f"HTTP_{exc.status_code}",
            context={
                "request_url": str(request.url),
                "request_method": request.method
            }
        )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=api_error.to_dict()
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    error_id = f"error_{datetime.timestamp}"
    
    logger.error(
        f"Unhandled exception [{error_id}]: {str(exc)}",
        extra={
            "error_id": error_id,
            "request_url": str(request.url),
            "request_method": request.method,
            "exception_type": type(exc).__name__,
            "stack_trace": traceback.format_exc()
        }
    )
    
    api_error = ErrorFactory.internal_server_error(
        user_message="An unexpected error occurred.",
        log_message=f"Unhandled exception: {str(exc)}",
        error_code="UNHANDLED_EXCEPTION",
        context={
            "error_id": error_id,
            "request_url": str(request.url),
            "request_method": request.method,
            "exception_type": type(exc).__name__,
        }
    )
    
    return JSONResponse(
        status_code=500,
        content=api_error.to_dict()
    )


@app.on_event("startup")
async def startup_event():
    """Application startup tasks"""
    logger.info("Application starting up...")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown tasks"""
    logger.info("Application shutting down...")
    engine.dispose()



@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests for debugging purposes"""
    start_time = datetime.now(timezone.utc)
    
    try:
        response = await call_next(request)
        process_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        logger.info(
            f"{request.method} {request.url} - {response.status_code} - {process_time:.3f}s"
        )
        
        return response
    except Exception as e:
        process_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        logger.error(
            f"{request.method} {request.url} - ERROR: {str(e)} - {process_time:.3f}s"
        )
        raise