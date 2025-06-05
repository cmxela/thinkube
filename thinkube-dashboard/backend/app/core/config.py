# app/core/config.py
from typing import List, Optional, Union
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, validator


class Settings(BaseSettings):
    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "K8s Dashboard Hub"
    
    # CORS settings
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Keycloak settings
    KEYCLOAK_URL: str
    KEYCLOAK_REALM: str
    KEYCLOAK_CLIENT_ID: str
    KEYCLOAK_CLIENT_SECRET: str
    KEYCLOAK_VERIFY_SSL: bool = True
    
    # Dashboard service URLs 
    MINIO_URL: str = "https://minio.k8s.cmxela.com"
    OPENSEARCH_URL: str = "https://osd.k8s.cmxela.com"
    HARBOR_URL: str = "https://registry.cmxela.com"
    QDRANT_URL: str = "https://qdrantc.k8s.cmxela.com"
    AWX_URL: str = "https://awx.k8s.cmxela.com"
    PGADMIN_URL: str = "https://pgadm.k8s.cmxela.com"
    DEVPI_URL: str = "https://devpi.k8s.cmxela.com"
    JUPYTERHUB_URL: str = "https://jupyterhub.k8s.cmxela.com"
    CODE_SERVER_URL: str = "https://code-server.k8s.cmxela.com"
    MKDOCS_URL: str = "https://docs.k8s.cmxela.com"

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()