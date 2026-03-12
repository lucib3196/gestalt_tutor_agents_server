from firebase_admin import storage
from pathlib import Path
from .fb_initialization import initialize_firebase_app
from langchain_google_community import GCSDirectoryLoader
initialize_firebase_app()
bucket = storage.bucket()
print(bucket.name)
blob = bucket.blob("me135/test.pdf")
with open(r"data\Lecture_01_27.pdf", "rb") as f:
    blob.upload_from_file(f)


