# paststack

CLI to generate production-ready FastAPI backends (uv, SQLite/Postgres, optional SQLModel, slowapi).

## Install (PyPI)

```bash
pip install -U paststack
paststack
```

Le questionnaire lit **directement stdin/stdout** (fiable dans le terminal intégré VS Code / Cursor). Pour l’UI **questionary** à la place : `PASTSTACK_USE_QUESTIONARY=1 paststack`.

## Develop

```bash
git clone https://github.com/initd-fr/paststack.git
cd paststack
uv sync
uv pip install -e .
paststack
```

## Tests

```bash
uv sync --group dev
uv run pytest tests/ -q
```

MIT License.
