# {{ project_name }}

Projet généré avec [create-fastapi-app](https://github.com/initd-fr/create-fastapi-app).

## Structure

- `src/app/core/` — configuration (`pydantic-settings`)
- `src/app/api/` — routeurs FastAPI, dépendances, routes
- `src/app/models/` — modèles ORM (rempli selon le choix SQLAlchemy / SQLModel)
- `src/app/schemas/` — schémas Pydantic pour l’API
- `src/app/database.py` — couche base de données (fichier fourni par le générateur selon SQLite / PostgreSQL / etc.)

## Lancer en dev

```bash
uv sync
cp .env.example .env
uv run uvicorn app.main:app --reload --app-dir src
```

Documentation interactive : http://127.0.0.1:8000/docs

## Qualité

```bash
uv sync --group dev
uv run ruff check src
uv run mypy src
```
