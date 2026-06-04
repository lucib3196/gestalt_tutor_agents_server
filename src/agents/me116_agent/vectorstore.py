from langchain_astradb import AstraDBVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from src.core.settings import get_settings
from src.document_loaders.firebase_loader import (
    FirebaseLectureDocumentLoader,
    FBHomeworkDocumentLoader,
)
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
    collection_name="me116_lecture_fb",
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
    for i in range(1, 9):
        if i == 6:
            continue
        
        prefix =f"me116_spring_2026/homework/homework{i}"
        docs = FBHomeworkDocumentLoader(
            key="questions",
            prefix=prefix,
            metadata={"course": "me116_spring2026", "homework": str(i)},
        ).load()

        results = await get_all_documents(docs)

        new_docs = results.new_docs
        updated_docs = results.updated_docs

        print(f"Summary: New Docs {len(new_docs)}, Docs to update {len(updated_docs)}")
        example = new_docs[0] if new_docs else updated_docs[0] if updated_docs else []
        print("Here is a new doc\n\n", example, "\n\n")
        answer = input("Continue? [y/N]: ").strip().lower()
        if answer in ("y", "yes"):
            print("Continuing...")
            if new_docs:
                await vector_store.aadd_documents(new_docs)

            if updated_docs:
                documents = [d for d, _ in updated_docs]
                ids = [id for _, id in updated_docs]

                await vector_store.aadd_documents(documents=documents, ids=ids)
        else:
            print("Cancelled.")
            exit()


if __name__ == "__main__":
    asyncio.run(main())
