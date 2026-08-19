from dataclasses import dataclass
from typing import Callable, Sequence, Literal

from langchain_core.documents import Document
from src.document_loaders.firebase_loader import FirebaseLectureDocumentLoader
from src.document_loaders.firebase_loader import FBHomeworkDocumentLoader


@dataclass(frozen=True)
class VectorstoreIngestionConfig:
    key: str
    collection_name: Literal["me118_lecture_fb", "me116_lecture_fb"]
    course: str
    load_documents: Callable[[], Sequence[Document]]
    require_confirmation: bool = True


def load_me116_docs():
    return FirebaseLectureDocumentLoader(
        prefix="me116_spring_2026/lectures",
        metadata={"course": "me116_spring2026"},
    ).load_and_split()


def load_me116_homework():
    return FBHomeworkDocumentLoader(
        key="questions",
        prefix="me116_spring_2026/homework/homework9",
        metadata={"course": "me116_spring2026"},
    ).load()


def load_me118_docs():
    return FirebaseLectureDocumentLoader(
        prefix="me118_winter_2026/lectures",
        metadata={"course": "me118_winter2026"},
    ).load_and_split()


INGESTION_CONFIGS = {
    "me116": VectorstoreIngestionConfig(
        key="me116",
        collection_name="me116_lecture_fb",
        course="me116_spring2026",
        load_documents=load_me116_docs,
    ),
    "me116_hw": VectorstoreIngestionConfig(
        key="me116",
        collection_name="me116_lecture_fb",
        course="me116_spring2026",
        load_documents = load_me116_homework
    ),
    "me118": VectorstoreIngestionConfig(
        key="me118",
        collection_name="me118_lecture_fb",
        course="me118_winter2026",
        load_documents=load_me118_docs,
    ),
}
