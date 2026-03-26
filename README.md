# create-fastapi-app

![logo](./img/logo.png)

CLI project in active development to scaffold clean FastAPI applications with a structured and opinionated setup.

![python](https://img.shields.io/badge/python-3.12%2B-blue)
![ruff](https://img.shields.io/badge/ruff-linting-red)
![mypy](https://img.shields.io/badge/mypy-typing-blue)
![license](https://img.shields.io/badge/license-MIT-green)

---

## Overview

create-fastapi-app is a Python CLI project designed to standardize and accelerate the creation of backend services using FastAPI.

The goal is to provide a clean, maintainable starting point with modern tooling and strong conventions.

---

## Project Status

> **Work in progress**

The CLI foundations and interactive configuration flow are implemented.  
FastAPI project generation is currently under development.

---

## Current Scope

What is currently available:

- Interactive CLI entrypoint (`create-fastapi-app`)
- Project configuration wizard (project name, stack options, etc.)
- Typed configuration models
- Restart / validation flow before generation
- Linting with Ruff
- Static typing with Mypy

---

## What it does today

The CLI currently allows you to:

- run an interactive setup wizard
- define the structure and options of a future FastAPI project
- iterate on configuration before generation is implemented

Example:

```bash
create-fastapi-app
```

## Planned Features

- FastAPI project scaffolding (file and folder generation)
- Multiple architecture templates (minimal, modular, clean architecture)
- Environment configuration
- Optional database setup (SQLite, PostgreSQL, pgvector)
- ORM integration (SQLAlchemy, SQLModel)
- Async task systems (background tasks, Celery, Arq)
- Rate limiting setup
- Git initialization and commit tooling
- Dependency installation automation

## Development Setup

### Clone the repository and install dependencies:

```bash
git clone https://github.com/initd-fr/create-fastapi-app.git
cd create-fastapi-app
uv sync
```

### Install locally in editable mode:

```bash
uv pip install -e .
```

### Run the CLI:

```bash
create-fastapi-app
```

## Code Quality

Before committing, ensure code quality:

```bash
uv run ruff check .
uv run mypy .
```

## Contributing

Contributions are welcome — but must follow the project’s standards.

Before opening a pull request:

- keep changes focused and minimal
- respect the existing project structure
- ensure code is typed and linted
- follow commit conventions

### Commit Convention

This project uses a structured commit format:

```
TYPE description (scope)
```

**Types:**

| Type | Description |
|------|-------------|
| `INIT` | Initial setup |
| `FEAT` | New feature |
| `FIX` | Bug fix |
| `CHORE` | Maintenance / tooling |
| `REFACTOR` | Code improvement without behavior change |
| `STYLE` | Formatting / lint fixes |
| `BUILD` | Packaging / release |

**Scopes:** `cli`, `generator`, `template`, `config`, `dependencies`, `typing`, `lint`, `docs`

Example:

```
FEAT add CLI question flow (cli)
```

## Roadmap

- [x] CLI initialization
- [x] Interactive configuration flow
- [x] Typing and linting setup
- [ ] FastAPI project generation
- [ ] Architecture templates
- [ ] Configuration system
- [ ] PyPI release

## Why this project

This project aims to:

- reduce friction when starting backend services
- enforce best practices early
- provide a consistent development baseline
- improve long-term maintainability

## License

MIT
