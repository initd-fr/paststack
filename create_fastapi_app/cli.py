import subprocess
from pathlib import Path
from shutil import copyfile

import click
import questionary

from create_fastapi_app.banner import display_banner
from create_fastapi_app.models import Project
from create_fastapi_app.prompts import ask_questions, show_summary

TEMPLATES_ROOT = Path(__file__).resolve().parent / "templates"
BASE = TEMPLATES_ROOT / "base"
DATABASE = TEMPLATES_ROOT / "database"
ORM = TEMPLATES_ROOT / "orm"
RATE_LIMITING = TEMPLATES_ROOT / "rate_limiting"


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


def _copy_and_render(template: Path, destination: Path, project: Project) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    copyfile(template, destination)
    content = destination.read_text()
    content = content.replace("{{ project_name }}", project.project_name)
    origins = project.allowed_origins or []
    content = content.replace("{{ allowed_origins }}", repr(origins))
    content = content.replace("{{project.allowed_origins}}", repr(origins))
    content = content.replace("{{ database }}", project.database.value)
    content = content.replace("{{ orm }}", project.orm.value)
    destination.write_text(content)


def _copy_template_tree(template_dir: Path, dest_root: Path, project: Project) -> None:
    if not template_dir.is_dir():
        return
    for path in sorted(template_dir.rglob("*")):
        if path.is_file():
            rel = path.relative_to(template_dir)
            _copy_and_render(path, dest_root / rel, project)


def setup_project(project: Project) -> None:
    main_directory = Path(project.project_name)

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

    _copy_template_tree(BASE, main_directory, project)

    venv_path = main_directory / project.project_name
    subprocess.run(["python", "-m", "venv", str(venv_path)], check=True)
