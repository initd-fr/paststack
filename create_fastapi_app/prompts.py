import click
import questionary

from create_fastapi_app.models import AsyncTask, Database, Orm, PackageManager, Project


def ask_questions() -> Project:
    project_name = questionary.text("What will your project be called ?").unsafe_ask()

    if not project_name:
        project_name = "my_fastapi_app"

    raw_package_manager: str = questionary.select(
        "Which package manager do you want to use ?",
        choices=[e.value for e in PackageManager],
    ).unsafe_ask()
    raw_database: str = questionary.select(
        "Which database do you want to use ?", choices=[e.value for e in Database]
    ).unsafe_ask()

    if raw_database != "none":
        raw_orm: str = questionary.select(
            "Which ORM do you want to use ?", choices=[e.value for e in Orm]
        ).unsafe_ask()
    else:
        raw_orm = "none"

    raw_async_task: str = questionary.select(
        "Do you need background task processing ?",
        choices=[e.value for e in AsyncTask],
    ).unsafe_ask()

    rate_limiting: bool = questionary.confirm("Enable rate limiting ?").unsafe_ask()
    config: bool = questionary.confirm(
        "Use environment configuration (.env) ?"
    ).unsafe_ask()
    git: bool = questionary.confirm("Initialize a git repository?").unsafe_ask()
    git_z: bool = questionary.confirm("Use Git-z ?").unsafe_ask()
    run_install: bool = questionary.confirm(
        "Would you like us to run install ?"
    ).unsafe_ask()

    package_manager = PackageManager(raw_package_manager)
    database = Database(raw_database)
    orm = Orm(raw_orm)
    async_task = AsyncTask(raw_async_task)

    project = Project(
        project_name=project_name,
        package_manager=package_manager,
        database=database,
        orm=orm,
        async_task=async_task,
        rate_limiting=rate_limiting,
        config=config,
        git=git,
        git_z=git_z,
        run_install=run_install,
    )

    return project


def show_summary(project: Project) -> None:
    click.echo()
    click.echo(f"Project : {project.project_name}")
    click.echo(f"Package Manager : {project.package_manager.value}")
    click.echo(f"Database : {project.database.value}")
    click.echo(f"ORM : {project.orm.value}")
    click.echo(f"Background task processing : {project.async_task.value}")
    click.echo(f"Enable rate limiting : {'yes' if project.rate_limiting else 'no'}")
    click.echo(f"Use environment configuration : {'yes' if project.config else 'no'}")
    click.echo(f"Initialize a git repository : {'yes' if project.git else 'no'}")
    click.echo(f"Use Git-z : {'yes' if project.git_z else 'no'}")
    click.echo(
        f"Would you like us to run install ? : {'yes' if project.run_install else 'no'}"
    )
    click.echo()
