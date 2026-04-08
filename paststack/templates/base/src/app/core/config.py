from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Variables lues depuis l’environnement (fichier `.env` à la racine du projet)."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "{{ project_name }}"
    debug: bool = False

    cors_origins: list[str] = {{ allowed_origins }}

    # URL async (SQLite ou Postgres) ; sans base de données, la valeur n’est pas utilisée
    database_url: str = "{{ database_url }}"


settings = Settings()
