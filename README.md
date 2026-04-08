# paststack

CLI to generate production-ready FastAPI backends (uv, SQLite/Postgres, optional SQLModel, slowapi).

## Install (PyPI)

```bash
pip install -U paststack
paststack
```

Le questionnaire utilise **`/dev/tty`** sur macOS/Linux quand c’est possible (contourne un stdin incorrect du terminal VS Code / Cursor). Forcer stdin : `PASTSTACK_USE_STDIN=1 paststack`. **Questionary** : `PASTSTACK_USE_QUESTIONARY=1 paststack`.

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
