from dataclasses import dataclass
from typing import Any, List
from functools import lru_cache
from langchain_astradb import AstraDBVectorStore
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from src.core.settings import get_settings
from src.ingestion.config import VectorstoreIngestionConfig
from src.agents.me116_agent.vectorstore import vector_store


@dataclass
class IngestionPlan:
    new_docs: List[Document]
    updated_docs: list[tuple[Document, Any]]
    skipped_docs: list[Document]


@dataclass
class IngestionResult:
    collection_name: str
    added: int
    updated: int
    skipped: int


@lru_cache
def get_vectorstore(collection_name: str) -> AstraDBVectorStore:
    settings = get_settings()
    embeddings = GoogleGenerativeAIEmbeddings(model=settings.embedding_model)
    return AstraDBVectorStore(
        collection_name=collection_name,
        embedding=embeddings,
        api_endpoint=settings.ASTRA_DB_API_ENDPOINT,
        token=settings.ASTRA_DB_APPLICATION_TOKEN,
    )


async def build_ingestion_plan(
    vector_store: AstraDBVectorStore, docs: List[Document]
) -> IngestionPlan:
    new_docs = []
    updated_docs = []
    skipped_docs = []
    for doc in docs:
        if not doc.id:
            raise ValueError(f"Document does not contain an id: {doc}")

        existing_doc = await vector_store.aget_by_document_id(doc.id)

        if not existing_doc:
            new_docs.append(doc)
        elif existing_doc.metadata != doc.metadata:
            updated_docs.append((doc, doc.id))
        else:
            skipped_docs.append(doc)

    return IngestionPlan(
        new_docs=new_docs,
        updated_docs=updated_docs,
        skipped_docs=skipped_docs,
    )


async def sync_vectorstore(
    config: VectorstoreIngestionConfig,
    *,
    dry_run: bool = False,
) -> IngestionResult:
    vector_store = get_vectorstore(config.collection_name)
    docs = list(config.load_documents())

    plan = await build_ingestion_plan(vector_store, docs)

    if dry_run:
        return IngestionResult(
            collection_name=config.collection_name,
            added=len(plan.new_docs),
            updated=len(plan.updated_docs),
            skipped=len(plan.skipped_docs),
        )

    if plan.new_docs:
        await vector_store.aadd_documents(plan.new_docs)

    if plan.updated_docs:
        documents = [doc for doc, _ in plan.updated_docs]
        ids = [doc_id for _, doc_id in plan.updated_docs]
        await vector_store.aadd_documents(documents=documents, ids=ids)

    return IngestionResult(
        collection_name=config.collection_name,
        added=len(plan.new_docs),
        updated=len(plan.updated_docs),
        skipped=len(plan.skipped_docs),
    )
