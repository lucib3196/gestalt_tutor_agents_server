
from langchain_astradb import AstraDBVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from src.core.settings import get_settings
from src.document_loaders.firebase_loader import FirebaseLectureDocumentLoader
import asyncio
from typing import List
from langchain_core.documents import Document
from dataclasses import dataclass
from typing import Any, Tuple


@dataclass
class RetrievedDocuments:
    new_docs: List[Document]
    updated_docs: List[Tuple[Document, Any]]


settings = get_settings()
embeddings = GoogleGenerativeAIEmbeddings(model=settings.embedding_model)
vector_store = AstraDBVectorStore(
    collection_name="me118_lecture_fb",
    embedding=embeddings,
    api_endpoint=settings.ASTRA_DB_API_ENDPOINT,
    token=settings.ASTRA_DB_APPLICATION_TOKEN,
)


async def get_all_documents(docs: List[Document]) -> RetrievedDocuments:
    updated_docs = []
    new_docs = []
    for d in docs:
        doc_id = d.id
        if not doc_id:
            raise ValueError(f"Document does not contain an id {d}")
        existing_doc = await vector_store.aget_by_document_id(doc_id)
        if existing_doc:
            if not existing_doc.metadata == d.metadata:
                updated_docs.append((d, doc_id))
            else:
                print("Skipping doc. Metadata is the same")
            continue
        # Found new doc
        else:

            new_docs.append(d)
    return RetrievedDocuments(new_docs=new_docs, updated_docs=updated_docs)


async def main():

    docs = FirebaseLectureDocumentLoader(
        prefix="me118_winter_2026/lectures"
    ).load_and_split()

    results = await get_all_documents(docs)

    new_docs = results.new_docs
    updated_docs = results.updated_docs

    print(f"Summary: New Docs {len(new_docs)}, Docs to update {len(updated_docs)}")

    if new_docs:
        await vector_store.aadd_documents(new_docs)

    if updated_docs:
        documents = [d for d, _ in updated_docs]
        ids = [id for _, id in updated_docs]

        await vector_store.aadd_documents(documents=documents, ids=ids)


if __name__ == "__main__":
    asyncio.run(main())
