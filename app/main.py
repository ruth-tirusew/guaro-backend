from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.config import settings, fastapi_config
from app.database import Base, engine, get_db
from app.dependencies import register_auth_adapter
from app.adapters.authentication.keycloak import KeycloakAdapter
from app.modules.authentication.router import router as authentication_router
from app.modules.authentication.provider import authentication_service_factory
from app.dependencies import register_auth_service


register_auth_adapter(lambda: KeycloakAdapter(
    server_url=settings.KEYCLOAK_URL,
    client_id=settings.KEYCLOAK_CLIENT_ID,
    client_secret=settings.KEYCLOAK_CLIENT_SECRET,
    realm=settings.KEYCLOAK_REALM
))

register_auth_service(authentication_service_factory)


app = FastAPI(**fastapi_config)

Base.metadata.create_all(bind=engine)

@app.on_event("shutdown")
def shutdown_db_client():
    engine.dispose()


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
    allow_credentials=True,
)

app.include_router(authentication_router, prefix="/api/v1")
