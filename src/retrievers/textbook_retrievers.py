from __future__ import annotations
from dataclasses import dataclass
from typing import Literal, TypeAlias
from src.core.settings import get_settings
from langchain_astradb import AstraDBVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings


settings = get_settings()


@dataclass(frozen=True)
class TextbookConfig:
    key: str
    collection_name: str
    description: str


VALID_TEXTBOOK: TypeAlias = Literal[
    "calculus_openstax",
    "fluid_mechanics_pdf",
    "physics_v1_openstax",
    "math_2562_libretext_diff_eq_with_linear_algebra",
]
TEXTBOOKS: dict[VALID_TEXTBOOK, TextbookConfig] = {
    "calculus_openstax": TextbookConfig(
        key="calculus_openstax",
        collection_name="calculus_openstax",
        description="Calculus (OpenStax)",
    ),
    "fluid_mechanics_pdf": TextbookConfig(
        key="fluid_mechanics_pdf",
        collection_name="fluid_mechanics_pdf",
        description="Fluid Mechanics (PDF)",
    ),
    "physics_v1_openstax": TextbookConfig(
        key="physics_v1_openstax",
        collection_name="physics_v1_openstax",
        description="Physics v1 (OpenStax)",
    ),
    "math_2562_libretext_diff_eq_with_linear_algebra": TextbookConfig(
        key="math_2562_libretext_diff_eq_with_linear_algebra",
        collection_name="math_2562_libretext_diff_eq_with_linear_algebra",
        description="Diff Eq + Linear Algebra (LibreTexts)",
    ),
}


def init_vectorstores() -> dict[VALID_TEXTBOOK, AstraDBVectorStore]:
    embeddings = GoogleGenerativeAIEmbeddings(model=settings.embedding_model)
    stores: dict[VALID_TEXTBOOK, AstraDBVectorStore] = {}
    failures: list[str] = []

    for tb, tb_info in TEXTBOOKS.items():
        try:
            vs = AstraDBVectorStore(
                collection_name=tb_info.collection_name,
                embedding=embeddings,
                api_endpoint=settings.ASTRA_DB_API_ENDPOINT,
                token=settings.ASTRA_DB_APPLICATION_TOKEN,
            )
            stores[tb] = vs
        except Exception as e:
            failures.append(f"{tb_info.key} ({tb_info.collection_name}): {e}")
    if failures:
        joined = "\n".join(f"- {x}" for x in failures)
        raise RuntimeError(f"Failed to initialize some vectorstores:\n{joined}")
    return stores


if __name__ == "__main__":
    print("Initializing textbook vectorstores...")
    stores = init_vectorstores()
    retriever = stores["calculus_openstax"]

    print(f"Loaded {len(stores)} textbooks: {', '.join(stores.keys())}")

    # quick smoke test
    query = "What is a differential equation?"
    docs = retriever.similarity_search(query)
    print(f"\nQuery: {query}")
    print(f"Top docs: {len(docs)}")
    if docs:
        print(docs[0].page_content)
