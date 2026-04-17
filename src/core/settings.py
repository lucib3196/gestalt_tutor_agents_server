from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Literal, Optional

from dotenv import load_dotenv
from pydantic import Field, model_validator
from pydantic_settings import BaseSettings


# Load .env variables before settings are instantiated.
load_dotenv()

ROOT_PATH = Path(__file__).parents[2].as_posix()
ENV = Literal["dev", "production"]
FB_ENV = Literal["emulator", "production"]


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # AI model configuration
    model: str = "gemini-2.5-flash"
    embedding_model: str = "gemini-embedding-001"
    mode: ENV = Field(alias="ENV", default="dev")
    prompt_source: Optional[Literal["local", "production"]] = None

    # External service keys
    GOOGLE_API_KEY: str | None = None
    LANGSMITH_API_KEY: str | None = None
    LANGSMITH_PROJECT: str | None = None

    # Vectordatabase
    ASTRA_DB_API_ENDPOINT: str | None = None
    ASTRA_DB_APPLICATION_TOKEN: str | None = None

    # FIREBASE Initalization
    FIREBASE_MODE: FB_ENV | None = "emulator"
    FIREBASE_CRED: str | None = None
    STORAGE_EMULATOR_HOST: str | None = None
    STORAGE_BUCKET: str | None = None
    FIREBASE_AUTH_EMULATOR_HOST: str | None = None

    PROJECT_ROOT: str = ROOT_PATH

    @model_validator(mode="after")
    def validate_required_runtime_fields(self):
        """Ensure core runtime secrets and endpoints are present."""
        required_fields = [
            "GOOGLE_API_KEY",
            "LANGSMITH_PROJECT",
            "FIREBASE_CRED",
            "STORAGE_BUCKET",
            "ASTRA_DB_APPLICATION_TOKEN",
            "ASTRA_DB_API_ENDPOINT",
        ]
        missing = []
        for field in required_fields:
            if not getattr(self, field):
                missing.append(field)

        if missing:
            raise RuntimeError(f"Missing required settings: {', '.join(missing)}")
        return self

    @model_validator(mode="after")
    def validate_emulators(self):
        """Validate emulator compatibility for runtime environment."""
        if self.mode == "production" and self.FIREBASE_MODE == "emulator":
            raise ValueError("Cannot use firebase emulators while ENV is production")

        if self.FIREBASE_MODE == "emulator" and not self.STORAGE_EMULATOR_HOST:
            raise RuntimeError(
                "STORAGE_EMULATOR_HOST must be set when FIREBASE_MODE=emulator"
            )

        return self

    @model_validator(mode="after")
    def format_credentials(self):
        """Load Firebase credentials from JSON string or local file path."""
        try:
            if self.FIREBASE_CRED is None:
                raise ValueError("Firebase Credentials must be set")

            if self.mode == "production":
                # In production, FIREBASE_CRED should be a JSON string.
                self.FIREBASE_CRED = json.loads(self.FIREBASE_CRED)
                return self
            else:
                # In development, FIREBASE_CRED is treated as a relative file path.
                cred_path = (Path(self.PROJECT_ROOT) / self.FIREBASE_CRED).resolve()

                if not cred_path.exists():
                    raise ValueError(f"Credential file not found: {cred_path}")

                self.FIREBASE_CRED = json.loads(cred_path.read_text())

                return self
        except Exception as e:
            raise ValueError(f"Failed to load firebase credentials: {e}")


@lru_cache
def get_settings() -> Settings:
    """Return cached validated application settings."""
    if not Settings().model:  # type: ignore
        raise ValueError("Failed to load AI model. Must be set in ENV")
    return Settings()  # type: ignore


@lru_cache
def get_settings_pretty_print() -> str:
    """Return a readable summary of key runtime settings."""
    settings = get_settings()

    lines = [
        "=== Runtime Settings ===",
        f"ENV: {settings.mode}",
        f"Base Model: {settings.model}",
        f"Embedding Model: {settings.embedding_model}",
        f"Firebase Mode: {settings.FIREBASE_MODE}",
        f"Project Root: {settings.PROJECT_ROOT}",
        f"Storage Emulator Host: {settings.STORAGE_EMULATOR_HOST or '(not set)'}",
        f"Storage Bucket: {settings.STORAGE_BUCKET or '(not set)'}",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    print(get_settings_pretty_print())
