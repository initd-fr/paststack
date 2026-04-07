from enum import Enum

from pydantic import BaseModel


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


class Project(BaseModel):
    project_name: str
    package_manager: str
    use_typing: bool
    use_ruff: bool
    enable_cors: bool
    allowed_origins: list[str] | None = None
    database: Database
    orm: Orm
    rate_limiting: bool
    config: bool
    git: bool
    git_z: bool
    run_install: bool
