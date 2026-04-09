from pydantic_settings import BaseSettings
from pydantic import model_validator
from functools import lru_cache
from dotenv import load_dotenv
from pathlib import Path
from typing import Literal, Optional
import os
from src.core.logger import logger

load_dotenv()

ROOT_PATH = Path(__file__).parents[2].as_posix()


class Settings(BaseSettings):
    model: str = "gemini-2.5-flash"
    embedding_model: str = "gemini-embedding-001"

    # Development/Production Configuration
    mode: Literal["dev", "production"] = "dev"
    model_provider: str = "google_genai"
    prompt_source: Optional[Literal["local", "production"]] = None

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
        dev_required = [
            "GOOGLE_API_KEY",
            "LANGSMITH_API_KEY",
            "LANGSMITH_PROJECT",
            "FIREBASE_CRED",
            "STORAGE_BUCKET",
        ]
        prod_required = [
            "ASTRA_DB_APPLICATION_TOKEN",
            "ASTRA_DB_API_ENDPOINT",
        ]
        if self.mode == "dev":
            required_fields = dev_required + prod_required
        else:
            required_fields = prod_required
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

    @model_validator(mode="after")
    def validate_prompt_source(self):
        if self.prompt_source == "local" and self.mode == "production":
            raise ValueError(
                "Prompt source cannot be local during production environments"
            )
        if not self.prompt_source:
            logger.info("Prompt Source is not set attempting to resolve")

        # By Defalt always use the production
        if self.mode == "production":
            self.prompt_source = "production"
        elif self.mode == "dev":
            self.prompt_source = "production"
        return self


@lru_cache
def get_settings() -> Settings:
    if not Settings().model:  # type: ignore
        raise ValueError("Failed to load AI model. Must be set in ENV")
    return Settings()  # type: ignore


if __name__ == "__main__":
    print(get_settings())
