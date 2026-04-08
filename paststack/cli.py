import os
import subprocess
import sys
import time
from pathlib import Path
from shutil import copyfile, which

import click
import questionary
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
)

from paststack.banner import display_banner
from paststack.models import Database, Orm, Project
from paststack.prompts import ask_questions, show_summary

TEMPLATES_ROOT = Path(__file__).resolve().parent / "templates"
BASE = TEMPLATES_ROOT / "base"
DATABASE = TEMPLATES_ROOT / "database"
RATE_LIMITING = TEMPLATES_ROOT / "rate_limiting"


def _venv_python(venv_path: Path) -> Path:
    if sys.platform == "win32":
        return venv_path / "Scripts" / "python.exe"
    return venv_path / "bin" / "python"


def _database_url(project: Project) -> str:
    if project.database == Database.NONE:
        return "sqlite+aiosqlite:///./data/app.db"
    if project.database == Database.SQLITE:
        return "sqlite+aiosqlite:///./data/app.db"
    if project.orm == Orm.SQLMODEL:
        return "postgresql+asyncpg://app:app@127.0.0.1:5432/app"
    return "postgresql://app:app@127.0.0.1:5432/app"


def _env_database_block(project: Project) -> str:
    if project.database == Database.NONE:
        return "# Pas de base de données (DATABASE_URL ignoré)"
    return f"DATABASE_URL={_database_url(project)}"


def _build_extra(project: Project) -> dict[str, str]:
    extra: dict[str, str] = {
        "{{ database_url }}": _database_url(project),
        "{{ env_database_block }}": _env_database_block(project),
    }
    if project.rate_limiting:
        extra["{{ rate_limit_imports }}"] = (
            "from app.core.rate_limit import setup_rate_limiting\n"
        )
        extra["{{ rate_limit_setup }}"] = "setup_rate_limiting(app)\n"
    else:
        extra["{{ rate_limit_imports }}"] = ""
        extra["{{ rate_limit_setup }}"] = ""
    return extra


def _subprocess_env_without_venv() -> dict[str, str]:
    env = os.environ.copy()
    env.pop("VIRTUAL_ENV", None)
    return env


def _docker_compose_up_postgres(project_root: Path) -> bool:
    """Démarre le conteneur Postgres du projet. Retourne False si Docker indisponible ou échec."""
    if not (project_root / "docker-compose.yml").is_file():
        click.echo("Aucun docker-compose.yml — impossible de lancer PostgreSQL ici.", err=True)
        return False
    if which("docker") is None:
        click.echo(
            click.style(
                "La commande `docker` est introuvable.\n"
                "→ Installe Docker Desktop : https://www.docker.com/products/docker-desktop/\n"
                "→ Puis dans le projet : docker compose up -d",
                fg="red",
            ),
            err=True,
        )
        return False
    result = subprocess.run(
        ["docker", "compose", "up", "-d"],
        cwd=project_root,
        capture_output=True,
        text=True,
        env=_subprocess_env_without_venv(),
    )
    if result.returncode != 0:
        click.echo(click.style("docker compose up -d a échoué.", fg="red"), err=True)
        if result.stderr.strip():
            click.echo(result.stderr, err=True)
        if result.stdout.strip():
            click.echo(result.stdout, err=True)
        click.echo(
            click.style(
                "Vérifie que Docker Desktop est démarré (icône baleine active).\n"
                "Ensuite, à la main : docker compose up -d",
                fg="yellow",
            ),
            err=True,
        )
        return False
    click.echo(click.style("PostgreSQL : conteneur démarré (docker compose up -d).", fg="green"))
    return True


def _uv_extras(project: Project) -> list[str]:
    extras: list[str] = []
    if project.database == Database.SQLITE:
        extras.append(
            "sqlite-sqlmodel" if project.orm == Orm.SQLMODEL else "sqlite-none"
        )
    elif project.database == Database.POSTGRES:
        extras.append(
            "postgres-sqlmodel" if project.orm == Orm.SQLMODEL else "postgres-none"
        )
    if project.rate_limiting:
        extras.append("rate-limit")
    return extras


@click.command()
def main() -> None:
    try:
        display_banner()
        while True:
            project = ask_questions()
            show_summary(project)
            if questionary.confirm("Proceed with project setup ?").unsafe_ask():
                break
        setup_project(project)
    except KeyboardInterrupt:
        click.echo("\nAborted.")


def _create_directories(base: Path, paths: list[tuple[str, ...]]) -> None:
    for parts in paths:
        (base / Path(*parts)).mkdir(parents=True, exist_ok=True)


def _copy_and_render(
    template: Path,
    destination: Path,
    project: Project,
    extra: dict[str, str] | None = None,
) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    copyfile(template, destination)
    content = destination.read_text(encoding="utf-8")
    content = content.replace("{{ project_name }}", project.project_name)
    origins = project.allowed_origins or []
    content = content.replace("{{ allowed_origins }}", repr(origins))
    content = content.replace("{{project.allowed_origins}}", repr(origins))
    content = content.replace("{{ database }}", project.database.value)
    content = content.replace("{{ orm }}", project.orm.value)
    for key, value in (extra or {}).items():
        content = content.replace(key, value)
    destination.write_text(content, encoding="utf-8")


def _copy_template_tree(
    template_dir: Path,
    dest_root: Path,
    project: Project,
    extra: dict[str, str] | None = None,
) -> None:
    if not template_dir.is_dir():
        return
    for path in sorted(template_dir.rglob("*")):
        if path.is_file():
            rel = path.relative_to(template_dir)
            _copy_and_render(path, dest_root / rel, project, extra)


def setup_project(project: Project) -> None:
    main_directory = Path(project.project_name).resolve()

    try:
        main_directory.mkdir()
    except FileExistsError:
        click.echo(f"Directory '{main_directory}' already exists.")
        return
    except PermissionError:
        click.echo(f"Permission denied: unable to create '{main_directory}'.")
        return
    except OSError as e:
        click.echo(f"An error occurred: {e}")
        return

    extra = _build_extra(project)
    _copy_template_tree(BASE, main_directory, project, extra)

    db_dest = main_directory / "src" / "app" / "database.py"

    match (project.database, project.orm):
        case (Database.NONE, _):
            pass
        case (Database.SQLITE, Orm.NONE):
            _copy_and_render(
                DATABASE / "sqlite" / "none" / "database.py", db_dest, project, extra
            )
        case (Database.SQLITE, Orm.SQLMODEL):
            _copy_template_tree(
                DATABASE / "sqlite" / "sqlmodel",
                main_directory / "src" / "app",
                project,
                extra,
            )
        case (Database.POSTGRES, Orm.NONE):
            _copy_and_render(
                DATABASE / "postgres" / "none" / "database.py", db_dest, project, extra
            )
            _copy_and_render(
                DATABASE / "postgres" / "docker-compose.yml",
                main_directory / "docker-compose.yml",
                project,
                extra,
            )
        case (Database.POSTGRES, Orm.SQLMODEL):
            _copy_template_tree(
                DATABASE / "postgres" / "sqlmodel",
                main_directory / "src" / "app",
                project,
                extra,
            )
            _copy_and_render(
                DATABASE / "postgres" / "docker-compose.yml",
                main_directory / "docker-compose.yml",
                project,
                extra,
            )

    if project.rate_limiting:
        _copy_template_tree(RATE_LIMITING, main_directory, project, extra)

    venv_path = (main_directory / project.project_name).resolve()
    py_exe = _venv_python(venv_path).resolve()

    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(bar_width=40),
        TaskProgressColumn(),
        TextColumn(" "),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
    ) as progress:
        t_venv = progress.add_task("Création du venv…", total=1)
        subprocess.run(
            [sys.executable, "-m", "venv", str(venv_path)],
            check=True,
            env=_subprocess_env_without_venv(),
        )
        progress.update(t_venv, completed=1)

        if project.run_install:
            uv_extras = _uv_extras(project)
            cmd = ["uv", "sync", "-p", str(py_exe)]
            for e in uv_extras:
                cmd.append(f"--extra={e}")
            t_sync = progress.add_task("uv sync (dépendances)…", total=1)
            subprocess.run(
                cmd,
                cwd=main_directory,
                check=True,
                env=_subprocess_env_without_venv(),
            )
            progress.update(t_sync, completed=1)

    if project.git_z:
        subprocess.run(["git", "init"], cwd=main_directory, check=True)
        # --default : config git-z sans wizard interactif (sinon le CLI semble « figé »)
        result = subprocess.run(
            ["git", "z", "init", "--default"],
            cwd=main_directory,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            click.echo(
                "git z init a échoué (git-z installé ?). "
                "Voir https://github.com/ejpcmac/git-z",
                err=True,
            )
            if result.stderr:
                click.echo(result.stderr, err=True)
    elif project.git:
        subprocess.run(["git", "init"], cwd=main_directory, check=True)

    env_example = main_directory / ".env.example"
    env_dest = main_directory / ".env"
    if env_example.is_file() and not env_dest.is_file():
        copyfile(env_example, env_dest)
        click.echo("Fichier .env créé à partir de .env.example.")

    start_uvicorn = project.run_install and questionary.confirm(
        "Démarrer l’API maintenant (uvicorn --reload) ?",
        default=True,
    ).unsafe_ask()

    if start_uvicorn and project.database == Database.POSTGRES:
        if questionary.confirm(
            "Lancer PostgreSQL avec Docker (`docker compose up -d`) ?",
            default=True,
        ).unsafe_ask():
            if not _docker_compose_up_postgres(main_directory):
                start_uvicorn = questionary.confirm(
                    "Lancer uvicorn quand même ? (l’API échouera si Postgres n’est pas joignable.)",
                    default=False,
                ).unsafe_ask()
            else:
                time.sleep(2)
        else:
            click.echo(
                click.style(
                    "Sans conteneur Docker, assure-toi que Postgres tourne déjà "
                    "(même URL que dans `.env`), sinon le démarrage de l’API échouera.",
                    fg="yellow",
                )
            )
            start_uvicorn = questionary.confirm(
                "Lancer uvicorn quand même ?",
                default=False,
            ).unsafe_ask()

    if start_uvicorn:
        click.echo(
            click.style(
                "\n→ http://127.0.0.1:8000/docs  (Ctrl+C pour arrêter)\n",
                fg="green",
            )
        )
        subprocess.run(
            [
                "uv",
                "run",
                "--python",
                str(py_exe),
                "uvicorn",
                "app.main:app",
                "--reload",
                "--app-dir",
                "src",
            ],
            cwd=main_directory,
            env=_subprocess_env_without_venv(),
        )
