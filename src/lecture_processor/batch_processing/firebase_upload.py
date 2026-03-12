from src.firebase.fb_initialization import initialize_firebase_app
from pathlib import Path
from firebase_admin import storage
import json
import tempfile

initialize_firebase_app()


def remove_key(obj, key):
    if isinstance(obj, dict):
        obj.pop(key, None)
        for v in obj.values():
            remove_key(v, key)
    elif isinstance(obj, list):
        for v in obj:
            remove_key(v, key)

def upload_directory(local_dir: str | Path, remote_prefix: str = ""):
    bucket = storage.bucket()
    local_dir = Path(local_dir)

    try:
        for file in local_dir.rglob("*"):
            if not file.is_file():
                continue

            relative_path = file.relative_to(local_dir)
            blob_path = f"{remote_prefix}/{relative_path}".replace("\\", "/")
            blob = bucket.blob(blob_path)

            # Handle JSON cleanup
            if file.suffix == ".json":
                data = json.loads(file.read_text(encoding="utf-8"))

                remove_key(data, "pdf_bytes")

                # Upload cleaned JSON via temp file
                with tempfile.NamedTemporaryFile(
                    mode="w", suffix=".json", delete=False
                ) as tmp:
                    json.dump(data, tmp)
                    tmp_path = tmp.name

                blob.chunk_size = 5 * 1024 * 1024
                blob.upload_from_filename(tmp_path)

            else:
                blob.chunk_size = 5 * 1024 * 1024
                blob.upload_from_filename(str(file))

            print(f"Uploaded {file} → {blob_path}")

    except Exception as e:
        raise ValueError(f"Failed to upload: {e}")

if __name__ == "__main__":
    print("Running")
    upload_directory("data/me118/output", "me118_winter_2026/lectures")
