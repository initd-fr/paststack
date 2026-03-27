import platform
import subprocess
from pathlib import Path
from shutil import copyfile

import click
import questionary

from create_fastapi_app.banner import display_banner
from create_fastapi_app.models import Project, StructureChoice
from create_fastapi_app.prompts import ask_questions, show_summary


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
    copyfile(template, destination)
    content = destination.read_text()
    content = content.replace("{{ project_name }}", project.project_name)
    destination.write_text(content)


def setup_project(project: Project) -> None:
    base = Path(project.project_name)

    try:
        base.mkdir()
    except FileExistsError:
        click.echo(f"Directory '{base}' already exists.")
        return
    except PermissionError:
        click.echo(f"Permission denied: unable to create '{base}'.")
        return
    except OSError as e:
        click.echo(f"An error occurred: {e}")
        return

    if project.project_structure == StructureChoice.MODULAR:
        directories: list[tuple[str, ...]] = [
            ("app", "api", "routes"),
            ("app", "core"),
            ("app", "services"),
            ("app", "models"),
            ("app", "schemas"),
            ("app", "db"),
            ("app", "dependencies"),
        ]
        _create_directories(base, directories)
        _copy_and_render(
            template=Path("templates/modular/main.py"),
            destination=base / "app" / "main.py",
            project=project,
        )

    else:
        directories = [("app",), ("app", "core")]
        _create_directories(base, directories)
        _copy_and_render(
            template=Path("templates/minimal/main.py"),
            destination=base / "main.py",
            project=project,
        )

    venv_path = base / project.project_name
    subprocess.run(["python", "-m", "venv", str(venv_path)], check=True)

    system: str = platform.system()

    if system == "Windows":
        venv_python = venv_path / "Scripts" / "python.exe"
    else:
        venv_python = venv_path / "bin" / "python"
