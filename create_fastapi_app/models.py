from enum import Enum

from pydantic import BaseModel


class PackageManager(str, Enum):
    PIP = "pip"
    UV = "uv"


class Database(str, Enum):
    NONE = "none"
    SQLITE = "sqlite"
    POSTGRES = "postgres"
    POSTGRES_POOL = "postgres_pool"
    POSTGRES_VECTOR = "postgres_vector"


class Orm(str, Enum):
    NONE = "none"
    SQLALCHEMY = "sqlalchemy"
    SQLMODEL = "sqlmodel"


class AsyncTask(str, Enum):
    NONE = "none"
    BACKGROUND = "background"
    CELERY = "celery"
    ARQ = "arq"


class Project(BaseModel):
    project_name: str
    package_manager: PackageManager
    database: Database
    orm: Orm
    async_task: AsyncTask
    rate_limiting: bool
    config: bool
    git: bool
    git_z: bool
    run_install: bool
