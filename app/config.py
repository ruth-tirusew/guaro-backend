from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional,Any

class Settings(BaseSettings):
    CORS_ORIGINS: list[str] = ["*"]
    CORS_HEADERS: list[str] = ["*"]
    CORS_METHODS: list[str] = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]

    KEYCLOAK_REALM: str
    KEYCLOAK_URL: str
    KEYCLOAK_CLIENT_SECRET: str
    KEYCLOAK_CLIENT_ID:str


 
    DATABASE_URL: str = "sqlite:///./test.db"
    
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

def get_settings() -> Settings:
    return Settings()

settings = get_settings()

fastapi_config: dict[str, Any] = {
    "title": "Guaro API",
}