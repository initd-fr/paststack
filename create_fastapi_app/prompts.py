import click
import questionary

from create_fastapi_app.models import Database, Orm, Project


def ask_questions() -> Project:
    project_name = questionary.text(
        "Project name",
        default="my_fastapi_app",
    ).unsafe_ask()

    raw_allowed_origins: str = questionary.text(
        "Allowed origins (CORS) [comma-separated, empty = disabled]",
        default="",
    ).unsafe_ask()

    allowed_origins: list[str] = [
        origin.strip() for origin in raw_allowed_origins.split(",") if origin.strip()
    ]

    raw_database: str = questionary.select(
        "Database",
        choices=[e.value for e in Database],
        default="none",
    ).unsafe_ask()

    raw_orm: str = "none"
    if raw_database != "none":
        raw_orm = questionary.select(
            "ORM",
            choices=[e.value for e in Orm],
        ).unsafe_ask()

    rate_limiting: bool = questionary.confirm(
        "Enable rate limiting",
        default=False,
    ).unsafe_ask()

    run_install: bool = questionary.confirm(
        "Run install after setup",
        default=True,
    ).unsafe_ask()

    project = Project(
        project_name=project_name,
        package_manager="uv",
        use_typing=True,
        use_ruff=True,
        enable_cors=bool(allowed_origins),
        allowed_origins=allowed_origins,
        database=Database(raw_database),
        orm=Orm(raw_orm),
        rate_limiting=rate_limiting,
        config=True,
        git=True,
        git_z=False,
        run_install=run_install,
    )

    return project


def show_summary(project: Project) -> None:
    click.echo()
    click.echo(f"Project : {project.project_name}")
    click.echo(f"Package Manager : {project.package_manager}")

    click.echo(f"CORS enabled : {'yes' if project.enable_cors else 'no'}")
    if project.enable_cors:
        click.echo(f"Allowed origins : {project.allowed_origins}")

    click.echo(f"Database : {project.database.value}")
    click.echo(f"ORM : {project.orm.value}")
    click.echo(f"Rate limiting : {'yes' if project.rate_limiting else 'no'}")
    click.echo(f"Run install : {'yes' if project.run_install else 'no'}")
    click.echo()
