# app/api/router.py
from fastapi import APIRouter
from app.api import auth, dashboards

api_router = APIRouter()

# Include the routes from the different modules
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(dashboards.router, prefix="/dashboards", tags=["dashboards"])