from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Paramètres chargés depuis l’environnement (fichier `.env` optionnel)."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "{{ project_name }}"
    debug: bool = False

    # Remplacé par le CLI : liste d’origines CORS, ou [] si désactivé
    cors_origins: list[str] = {{ allowed_origins }}


settings = Settings()
