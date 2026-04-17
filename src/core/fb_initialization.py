from functools import lru_cache
import os
from pathlib import Path

import firebase_admin
from firebase_admin import credentials

from src.core.settings import get_settings


app_settings = get_settings()

# If a storage emulator is configured, expose it via env var for Firebase SDK usage.
if app_settings.STORAGE_EMULATOR_HOST:
    os.environ["STORAGE_EMULATOR_HOST"] = app_settings.STORAGE_EMULATOR_HOST


@lru_cache
def initialize_firebase_app():
    """Initialize Firebase app once and reuse it across calls."""
    try:
        cred = credentials.Certificate(app_settings.FIREBASE_CRED)

        return firebase_admin.initialize_app(
            cred,
            {"storageBucket": app_settings.STORAGE_BUCKET},
        )
    except Exception as e:
        raise ValueError(f"Could not initialize credentials error {str(e)}") from e


if __name__ == "__main__":
    # Quick local sanity check output.
    print("🔥 Firebase Mode:")
    print("Storage Emulator:", os.getenv("STORAGE_EMULATOR_HOST"))
    fb = initialize_firebase_app()
    print(fb)
