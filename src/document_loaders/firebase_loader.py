import json
from collections import defaultdict
from dataclasses import dataclass
from typing import DefaultDict, List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_text_splitters import TextSplitter

from firebase.fb_initialization import initialize_firebase_app
from firebase_admin import storage
from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document

from src.lecture_processor.lecture_analysis.model import LectureAnalysis


@dataclass
class LectureBundle:
    pdf: str | None = None
    md: str | None = None
    json: str | None = None


initialize_firebase_app()

class FirebaseLectureDocumentLoader(BaseLoader):
    """Load lecture markdown and metadata documents from Firebase Storage."""

    def __init__(
        self,
        prefix: str,
        recursive: bool = True,
        metadata: dict[str, str] | None = None,
        lecture_key: str = "lecture_summary",
    ):
        """Initialize the loader.

        Args:
            prefix: Storage path prefix that contains lecture subfolders.
            recursive: Included for loader compatibility; traversal is prefix-based.
            metadata: Base metadata merged into each emitted document.
            lecture_key: Key in each lecture JSON used to extract analysis metadata.
        """
        self.prefix = prefix
        self.recursive = recursive
        self.base_metadata = metadata or {}
        self.lecture_key = lecture_key
        self.bucket = storage.bucket()

    def bundle_lectures(self) -> DefaultDict[str, LectureBundle]:
        """Map lecture folder names to discovered PDF, markdown, and JSON blobs."""
        lectures = defaultdict(LectureBundle)
        for b in self.bucket.list_blobs(prefix=self.prefix):
            relative = b.name.removeprefix(self.prefix)
            lecture = relative.lstrip("/").split("/", 1)[0]
            if b.name.endswith(".pdf"):
                lectures[lecture].pdf = b.name
            elif b.name.endswith(".md"):
                lectures[lecture].md = b.name
            elif b.name.endswith(".json"):
                lectures[lecture].json = b.name
        return lectures

    def load(self) -> List[Document]:
        """Load complete lecture bundles as documents.

        Returns:
            A document per lecture containing markdown body and merged metadata.
            Lectures missing required files or valid metadata are skipped.
        """
        docs = []
        lecture_bundle = self.bundle_lectures()
        for title, contents in lecture_bundle.items():
            # Require all three lecture artifacts.
            if not contents.pdf or not contents.md or not contents.json:
                continue

            pdf_blob = self.bucket.blob(contents.pdf)
            md_blob = self.bucket.blob(contents.md)
            json_blob = self.bucket.blob(contents.json)
            # Skip stale references that no longer exist in storage.
            if not pdf_blob.exists() or not md_blob.exists() or not json_blob.exists():
                continue

            content = md_blob.download_as_string().decode("utf-8")
            raw_metadata = json.loads(json_blob.download_as_string())
            lecture_metadata = raw_metadata.get(self.lecture_key, {})
            if not lecture_metadata:
                continue

            lec_meta = LectureAnalysis.model_validate(lecture_metadata)
            pdf_path = pdf_blob.public_url
            md_path = md_blob.public_url

            # Create the id
            prefix_id = self.prefix.rstrip("/").replace("/", "_")
            lecture_id = title.lower()
            doc_id = f"{prefix_id}:{lecture_id}:0"

            docs.append(
                Document(
                    id=doc_id,
                    page_content=content,
                    metadata={
                        **self.base_metadata,
                        **lec_meta.model_dump(),
                        "source_pdf": pdf_path,
                        "source_markdown": md_path,
                    },
                )
            )

        return docs

    def load_and_split(
        self, text_splitter: TextSplitter | None = None
    ) -> List[Document]:
        """Load lectures and split them into chunked child documents.

        Args:
            text_splitter: Optional splitter. Defaults to recursive splitting.

        Returns:
            Chunked documents preserving parent metadata and chunk index.
        """
        if not text_splitter:
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=2000,
                chunk_overlap=100,
            )
        docs = self.load()
        chunked_docs = []
        for doc in docs:
            chunks = text_splitter.split_text(doc.page_content)
            for i, chunk in enumerate(chunks):
                chunked_docs.append(
                    Document(
                        id=f"{doc.id}:{i}",
                        page_content=chunk,
                        metadata={**doc.metadata, "parent_id": doc.id, "chunk": i},
                    )
                )
        return chunked_docs


if __name__ == "__main__":
    from langchain_core.vectorstores import InMemoryVectorStore
    from langchain_google_genai import GoogleGenerativeAIEmbeddings

    embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")
    vector_store = InMemoryVectorStore(embeddings)

    docs = FirebaseLectureDocumentLoader(prefix="me118_winter_2026/lectures").load()

    ids = vector_store.add_documents(docs)
    existing_ids = set(vector_store.store.keys())
    new_docs = []
    new_ids = []
    for doc in docs:
        doc_id = doc.id

        if doc_id in existing_ids:
            print("Skipping existing:", doc_id)
            continue

        new_docs.append(doc)
        new_ids.append(doc_id)

    if new_docs:
        vector_store.add_documents(new_docs, ids=new_ids)

