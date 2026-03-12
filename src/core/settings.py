from pydantic_settings import BaseSettings
from pydantic import model_validator
from functools import lru_cache
from dotenv import load_dotenv
from pathlib import Path
from typing import Literal
import os
from src.core.logger import logger

load_dotenv()

ROOT_PATH = Path(__file__).parents[2].as_posix()


class Settings(BaseSettings):
    model: str = "gemini-2.5-flash"
    embedding_model: str = "gemini-embedding-001"
    mode: Literal["dev", "production"] = "dev"
    GOOGLE_API_KEY: str | None = None
    LANGSMITH_API_KEY: str | None = None
    LANGSMITH_PROJECT: str | None = None

    # Vectordatabase
    ASTRA_DB_API_ENDPOINT: str | None = None
    ASTRA_DB_APPLICATION_TOKEN: str | None = None

    # FIREBASE Initalization
    FIREBASE_CRED: str | None = None
    STORAGE_EMULATOR_HOST: str | None = None
    STORAGE_BUCKET: str | None = None
    FIREBASE_AUTH_EMULATOR_HOST: str | None = None

    PROJECT_ROOT: str = ROOT_PATH

    @model_validator(mode="after")
    def validate_required_runtime_fields(self):
        required_fields = [
            "GOOGLE_API_KEY",
            "LANGSMITH_API_KEY",
            "LANGSMITH_PROJECT",
            "ASTRA_DB_APPLICATION_TOKEN",
            "ASTRA_DB_API_ENDPOINT",
            "FIREBASE_CRED",
            "STORAGE_BUCKET",
        ]
        missing = []
        for field in required_fields:
            if not getattr(self, field):
                missing.append(field)
        if missing:
            raise RuntimeError(f"Missing required settings: {', '.join(missing)}")
        return self

    @model_validator(mode="after")
    def validate_emulator(self):
        firebase_emulators = ["STORAGE_EMULATOR_HOST", "FIREBASE_AUTH_EMULATOR_HOST"]
        try:
            for v in firebase_emulators:
                if self.mode == "dev":
                    if not getattr(self, v):
                        raise RuntimeError(f"{v} must be set in Dev")
                elif self.mode == "production":
                    if getattr(self, v):
                        setattr(self, v, None)
                        os.environ.pop(v, None)
                else:
                    raise ValueError(f"Cannot determine mode {self.mode}")

            return self
        except Exception as e:
            raise


@lru_cache
def get_settings() -> Settings:
    if not Settings().model:  # type: ignore
        raise ValueError("Failed to load AI model. Must be set in ENV")
    return Settings()  # type: ignore


if __name__ == "__main__":
    print(get_settings())
