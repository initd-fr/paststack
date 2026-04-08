# {{ project_name }}

Projet généré avec [paststack](https://github.com/initd-fr/paststack).

## Structure

- `src/app/core/` — configuration (`pydantic-settings`)
- `src/app/api/` — routeurs, dépendances, routes
- `src/app/models/` — modèles **SQLModel** (si ORM activé)
- `src/app/schemas/` — schémas Pydantic pour l’API
- `src/app/database.py` — couche base (générée selon SQLite / Postgres, ORM ou non)

## Dépendances optionnelles

Le générateur installe les extras `uv` adaptés (ex. `sqlite-sqlmodel`, `postgres-none`, `rate-limit`).  
Pour réinstaller à la main :

```bash
uv sync --extra <nom>   # voir [project.optional-dependencies] dans pyproject.toml
```

## Lancer en dev

```bash
cp .env.example .env
uv run uvicorn app.main:app --reload --app-dir src
```

PostgreSQL : démarre la base avec `docker compose up -d` (fichier fourni si tu as choisi Postgres).

Documentation interactive : http://127.0.0.1:8000/docs

## Qualité

```bash
uv sync --group dev
uv run ruff check src
uv run mypy src
```
