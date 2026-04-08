import os
import sys

import click
import questionary

from paststack.models import Database, Orm, Project


def _write_line(message: str = "") -> None:
    sys.stdout.write(message + "\n")
    sys.stdout.flush()


def _read_line() -> str | None:
    """Lit une ligne ; None si EOF (stdin fermé / pipe vide)."""
    line = sys.stdin.readline()
    if line == "":
        return None
    return line.rstrip("\r\n")


def _prompt_text(label: str, default: str = "", *, show_default: bool = True) -> str:
    if show_default and default:
        sys.stdout.write(f"{label} [{default}]: ")
    else:
        sys.stdout.write(f"{label}: ")
    sys.stdout.flush()
    raw = _read_line()
    if raw is None:
        return default
    return raw if raw else default


def _prompt_confirm(message: str, default: bool = False) -> bool:
    hint = "Y/n" if default else "y/N"
    while True:
        sys.stdout.write(f"{message} [{hint}] ")
        sys.stdout.flush()
        raw = _read_line()
        if raw is None:
            return default
        s = raw.strip().lower()
        if not s:
            return default
        if s in ("y", "yes", "o", "oui"):
            return True
        if s in ("n", "no", "non"):
            return False
        _write_line("Réponds par y ou n (ou Entrée pour le défaut).")


def _prompt_int_range(label: str, lo: int, hi: int, default: int) -> int:
    while True:
        sys.stdout.write(f"{label} [{lo}-{hi}, défaut {default}]: ")
        sys.stdout.flush()
        raw = _read_line()
        if raw is None or raw.strip() == "":
            return default
        try:
            n = int(raw.strip(), 10)
        except ValueError:
            _write_line(f"Entre un entier entre {lo} et {hi}.")
            continue
        if lo <= n <= hi:
            return n
        _write_line(f"Entre un entier entre {lo} et {hi}.")


def use_simple_prompts() -> bool:
    """Par défaut : prompts `click` (fiables partout, dont terminal intégré VS Code / Cursor).

    Questionary (prompt_toolkit) uniquement si tu choisis explicitement :
    `PASTSTACK_USE_QUESTIONARY=1 paststack`
    """
    if os.environ.get("PASTSTACK_USE_QUESTIONARY", "").strip().lower() in ("1", "true", "yes", "on"):
        return False
    return True


def confirm(message: str, default: bool = False) -> bool:
    if use_simple_prompts():
        return _prompt_confirm(message, default=default)
    out = questionary.confirm(message, default=default).unsafe_ask()
    return bool(out)


def _pick_choice(label: str, values: list[str], *, default_value: str) -> str:
    _write_line()
    _write_line(label)
    default_idx = values.index(default_value) + 1 if default_value in values else 1
    for i, v in enumerate(values, start=1):
        mark = "*" if i == default_idx else " "
        _write_line(f"  [{i}]{mark} {v}")
    choice = _prompt_int_range("Numéro", 1, len(values), default_idx)
    return values[int(choice) - 1]


def _ask_questions_click() -> Project:
    _write_line(
        click.style("(saisie clavier — Entrée = défaut à chaque question)", fg="dim")
    )
    project_name = _prompt_text("Project name", "my_fastapi_app")
    raw_allowed_origins = _prompt_text(
        "Allowed origins (CORS), séparés par des virgules [vide = désactivé]",
        "",
        show_default=False,
    )
    allowed_origins = [o.strip() for o in raw_allowed_origins.split(",") if o.strip()]

    db_values = [e.value for e in Database]
    raw_database = _pick_choice("Base de données", db_values, default_value="none")

    raw_orm = "none"
    if raw_database != "none":
        orm_values = [e.value for e in Orm]
        raw_orm = _pick_choice(
            "Couche données (sqlmodel = ORM + Pydantic, none = driver seul)",
            orm_values,
            default_value="sqlmodel",
        )

    rate_limiting = _prompt_confirm("Activer le rate limiting ?", default=False)
    run_install = _prompt_confirm(
        "Lancer l’installation (uv sync) après la génération ?", default=True
    )
    git = _prompt_confirm("Initialiser un dépôt git dans le nouveau projet ?", default=True)
    git_z = False
    if git:
        git_z = _prompt_confirm(
            "Lancer git z init (git-z) ? — https://github.com/ejpcmac/git-z",
            default=False,
        )

    return Project(
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
        git=git,
        git_z=git_z,
        run_install=run_install,
    )


def _ask_questions_questionary() -> Project:
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
            "Data layer (SQLModel = ORM + Pydantic, none = driver only)",
            choices=[e.value for e in Orm],
            default="sqlmodel",
        ).unsafe_ask()

    rate_limiting: bool = questionary.confirm(
        "Enable rate limiting",
        default=False,
    ).unsafe_ask()

    run_install: bool = questionary.confirm(
        "Run install after setup",
        default=True,
    ).unsafe_ask()

    git: bool = questionary.confirm(
        "Initialize git repository in the new project?",
        default=True,
    ).unsafe_ask()

    git_z: bool = False
    if git:
        git_z = questionary.confirm(
            "Run git z init (git-z commit wizard)? Requires git-z — https://github.com/ejpcmac/git-z",
            default=False,
        ).unsafe_ask()

    return Project(
        project_name=project_name or "my_fastapi_app",
        package_manager="uv",
        use_typing=True,
        use_ruff=True,
        enable_cors=bool(allowed_origins),
        allowed_origins=allowed_origins,
        database=Database(raw_database or "none"),
        orm=Orm(raw_orm or "none"),
        rate_limiting=bool(rate_limiting),
        config=True,
        git=bool(git),
        git_z=bool(git_z),
        run_install=bool(run_install),
    )


def ask_questions() -> Project:
    if use_simple_prompts():
        return _ask_questions_click()
    return _ask_questions_questionary()


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
    click.echo(f"Git init : {'yes' if project.git else 'no'}")
    click.echo(f"git-z init : {'yes' if project.git_z else 'no'}")
    click.echo()
