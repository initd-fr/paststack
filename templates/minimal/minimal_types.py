from enum import Enum

from pydantic import BaseModel


class Status(str, Enum):
    RUNNING = "running"
    ERROR = "error"


class GetStatus(BaseModel):
    status: Status
    app_name: str
    app_version: str
    cpu_usage: float
    memory_usage: float
    docs_url: str
    redoc_url: str
    error: str | None = None
