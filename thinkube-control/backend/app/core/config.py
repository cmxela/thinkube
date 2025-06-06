# app/core/config.py
from typing import List, Optional, Union
from pydantic_settings import BaseSettings
from pydantic import field_validator, Field


class Settings(BaseSettings):
    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "K8s Dashboard Hub"
    
    # CORS settings - Field with mode='before' to process before JSON parsing
    BACKEND_CORS_ORIGINS: List[str] = Field(default_factory=list)

    @field_validator("BACKEND_CORS_ORIGINS", mode='before')
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        raise ValueError(v)
    
    # Keycloak settings
    KEYCLOAK_URL: str
    KEYCLOAK_REALM: str
    KEYCLOAK_CLIENT_ID: str
    KEYCLOAK_CLIENT_SECRET: str
    KEYCLOAK_VERIFY_SSL: bool = True
    
    # Frontend URL for redirects
    FRONTEND_URL: str
    
    # Dashboard service URLs - configured via environment variables
    SEAWEEDFS_URL: str
    HARBOR_URL: str
    GITEA_URL: str
    ARGOCD_URL: str
    ARGO_WORKFLOWS_URL: str
    # Services not yet deployed - uncomment when ready
    # OPENSEARCH_URL: str
    # QDRANT_URL: str
    # AWX_URL: str
    # PGADMIN_URL: str
    # DEVPI_URL: str
    # JUPYTERHUB_URL: str
    # CODE_SERVER_URL: str
    # MKDOCS_URL: str

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()