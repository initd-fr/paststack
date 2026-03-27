import os

import click
import questionary

from create_fastapi_app.banner import display_banner
from create_fastapi_app.models import Project
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
        # setup_project(project)
    except KeyboardInterrupt:
        click.echo("\nAborted.")


def setup_project(project: Project) -> None:
    directory_name = project.project_name

    try:
        os.makedirs(directory_name)
    except FileExistsError:
        click.echo(f"Directory '{directory_name}' already exists.")
    except PermissionError:
        click.echo(f"Permission denied: Unable to create '{directory_name}'.")
    except Exception as e:
        click.echo(f"An error occurred: {e}")
