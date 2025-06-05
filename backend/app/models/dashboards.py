# app/models/dashboards.py
from typing import List, Optional
from pydantic import BaseModel, HttpUrl


class DashboardItem(BaseModel):
    """Model for a dashboard item."""
    id: str
    name: str
    description: str
    url: HttpUrl
    icon: str
    color: str
    category: str
    requires_role: Optional[str] = None


class UserInfo(BaseModel):
    """Model for user information."""
    sub: str
    preferred_username: str
    email: Optional[str] = None
    name: Optional[str] = None
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    roles: List[str] = []


class Token(BaseModel):
    """Model for the token response."""
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: str
    refresh_expires_in: int


class AuthInfo(BaseModel):
    """Model for authentication info."""
    keycloak_url: str
    realm: str
    client_id: str
    auth_url: str
    token_url: str
    userinfo_url: str
    logout_url: str
    end_session_endpoint: str