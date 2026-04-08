"""Combinaisons valides du générateur — réutilisables par les tests ou d’autres outils."""

from __future__ import annotations

from collections.abc import Iterator

from paststack.models import Database, Orm, Project


def iter_database_orm_rate_limit_triples() -> Iterator[tuple[Database, Orm, bool]]:
    """Toutes les combinaisons métier valides (SGBD × ORM × rate limiting)."""
    for rate_limiting in (False, True):
        yield (Database.NONE, Orm.NONE, rate_limiting)

    for database in (Database.SQLITE, Database.POSTGRES):
        for orm in (Orm.NONE, Orm.SQLMODEL):
            for rate_limiting in (False, True):
                yield (database, orm, rate_limiting)


def make_project(
    database: Database,
    orm: Orm,
    *,
    rate_limiting: bool = False,
    project_name: str = "generated_app",
    run_install: bool = False,
    git: bool = False,
    git_z: bool = False,
) -> Project:
    """Construit un `Project` cohérent (sans base → ORM forcé à none)."""
    if database == Database.NONE:
        orm = Orm.NONE
    return Project(
        project_name=project_name,
        package_manager="uv",
        use_typing=True,
        use_ruff=True,
        enable_cors=False,
        allowed_origins=None,
        database=database,
        orm=orm,
        rate_limiting=rate_limiting,
        config=True,
        git=git,
        git_z=git_z,
        run_install=run_install,
    )


def iter_all_projects(
    *,
    project_name: str = "generated_app",
    run_install: bool = False,
) -> Iterator[Project]:
    """Itère un `Project` par combinaison valide."""
    for database, orm, rate_limiting in iter_database_orm_rate_limit_triples():
        yield make_project(
            database,
            orm,
            rate_limiting=rate_limiting,
            project_name=project_name,
            run_install=run_install,
        )


def combination_count() -> int:
    return sum(1 for _ in iter_database_orm_rate_limit_triples())
