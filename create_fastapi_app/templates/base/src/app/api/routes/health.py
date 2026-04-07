from fastapi import APIRouter

from app.database import is_database_configured

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
def ready() -> dict[str, str | bool]:
    return {"status": "ok", "database": is_database_configured()}
