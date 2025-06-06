# app/core/config.py
from typing import List, Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "K8s Dashboard Hub"
    
    # CORS settings
    BACKEND_CORS_ORIGINS: List[str] = []
    
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