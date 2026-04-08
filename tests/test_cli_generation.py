"""Tests de génération du projet pour chaque combinaison (fichiers + cohérence)."""

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from paststack.cli import setup_project
from paststack.combinations import (
    combination_count,
    iter_database_orm_rate_limit_triples,
    make_project,
)
from paststack.models import Database, Orm


def _noop_subprocess_run(*_args, **_kwargs) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess([], 0, "", "")


def _stub_confirm(*_args, **_kwargs) -> MagicMock:
    m = MagicMock()
    m.unsafe_ask.return_value = False
    return m


@pytest.fixture
def no_subprocess(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(subprocess, "run", _noop_subprocess_run)


@pytest.fixture
def no_server_prompt(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("paststack.cli.confirm", lambda *_a, **_k: False)


def test_combination_count_matches_iter() -> None:
    assert combination_count() == sum(
        1 for _ in iter_database_orm_rate_limit_triples()
    )
    assert combination_count() == 10


@pytest.mark.parametrize(
    ("database", "orm", "rate_limiting"),
    list(iter_database_orm_rate_limit_triples()),
)
def test_setup_project_generates_expected_layout(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    no_subprocess: None,
    no_server_prompt: None,
    database: Database,
    orm: Orm,
    rate_limiting: bool,
) -> None:
    monkeypatch.chdir(tmp_path)
    name = f"app_{database.value}_{orm.value}_{rate_limiting!s}".replace(".", "_")
    project = make_project(
        database,
        orm,
        rate_limiting=rate_limiting,
        project_name=name,
        run_install=False,
    )
    setup_project(project)

    root = tmp_path / name
    assert root.is_dir()
    assert (root / "pyproject.toml").read_text(encoding="utf-8")
    assert (root / "src" / "app" / "main.py").is_file()
    assert (root / "src" / "app" / "database.py").is_file()

    if database == Database.POSTGRES:
        assert (root / "docker-compose.yml").is_file()
    else:
        assert not (root / "docker-compose.yml").exists()

    if rate_limiting:
        assert (root / "src" / "app" / "core" / "rate_limit.py").is_file()
    else:
        assert not (root / "src" / "app" / "core" / "rate_limit.py").exists()

    db_text = (root / "src" / "app" / "database.py").read_text(encoding="utf-8")
    if database == Database.NONE:
        assert "is_database_configured" in db_text
        assert db_text.count("False") >= 1
    elif database == Database.SQLITE and orm == Orm.NONE:
        assert "aiosqlite" in db_text
    elif database == Database.SQLITE and orm == Orm.SQLMODEL:
        assert "SQLModel" in db_text or "sqlmodel" in db_text.lower()
    elif database == Database.POSTGRES and orm == Orm.NONE:
        assert "psycopg" in db_text.lower()
    elif database == Database.POSTGRES and orm == Orm.SQLMODEL:
        assert "SQLModel" in db_text or "sqlmodel" in db_text.lower()

    main_py = (root / "src" / "app" / "main.py").read_text(encoding="utf-8")
    if rate_limiting:
        assert "setup_rate_limiting" in main_py
    else:
        assert "setup_rate_limiting" not in main_py
