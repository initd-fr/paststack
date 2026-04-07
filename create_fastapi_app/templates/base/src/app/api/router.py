"""Routeur API versionnée — préfixe `/api/v1` dans `main`."""

from fastapi import APIRouter

api_router = APIRouter()
# Inclure ici les sous-routeurs métier (users, items, …) selon le générateur.
