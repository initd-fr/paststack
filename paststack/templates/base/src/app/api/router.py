"""Routeur racine de l’API (monté sous `/api/v1` dans `main.py`)."""

from fastapi import APIRouter

api_router = APIRouter()
# Branche tes routeurs métier : api_router.include_router(users.router, prefix="/users")
