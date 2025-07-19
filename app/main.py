from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from app.config import settings, fastapi_config
from app.database import Base, engine
from app.adapters.authentication.keycloak import KeycloakAdapter
from app.dependencies import init_containers

init_containers()

from app.modules.authentication.router import router as authentication_router
from app.modules.farmers.router import router as farmer_router
from app.modules.resources.router import router as resource_router
from app.modules.roles.router import router as role_router
from app.modules.users.router import router as user_router

app = FastAPI(**fastapi_config)

Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
    allow_credentials=True,
)

app.include_router(authentication_router, prefix="/api/v1")
app.include_router(farmer_router, prefix="/api/v1")
app.include_router(role_router, prefix="/api/v1")
app.include_router(resource_router, prefix="/api/v1")
app.include_router(user_router, prefix="/api/v1")

@app.on_event("shutdown")
def shutdown_db_client():
    engine.dispose()