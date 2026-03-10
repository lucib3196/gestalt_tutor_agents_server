from pydantic_settings import BaseSettings
from pydantic import model_validator
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    model: str = "gemini-2.5-flash"
    embedding_model: str = "gemini-embedding-001"

    GOOGLE_API_KEY: str | None = None
    LANGSMITH_API_KEY: str | None = None
    LANGSMITH_PROJECT: str | None = None

    ASTRA_DB_API_ENDPOINT: str | None = None
    ASTRA_DB_APPLICATION_TOKEN: str | None = None

    @model_validator(mode="after")
    def validate_required_runtime_fields(self):
        required_fields = [
            "GOOGLE_API_KEY",
            "LANGSMITH_API_KEY",
            "LANGSMITH_PROJECT",
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


@lru_cache
def get_settings() -> Settings:
    if not Settings().model:  # type: ignore
        raise ValueError("Failed to load AI model. Must be set in ENV")
    return Settings()  # type: ignore


if __name__ == "__main__":
    print(get_settings())
