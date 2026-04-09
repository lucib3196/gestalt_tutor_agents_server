from langchain_astradb import AstraDBVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from src.core.settings import get_settings
from src.document_loaders.gestalt_question_loader import QuestionModuleDocumentLoader


settings = get_settings()
embeddings = GoogleGenerativeAIEmbeddings(model=settings.embedding_model)


def get_vectorstore() -> AstraDBVectorStore:
    return AstraDBVectorStore(
        collection_name="gestalt_module",
        embedding=embeddings,
        api_endpoint=settings.ASTRA_DB_API_ENDPOINT,
        token=settings.ASTRA_DB_APPLICATION_TOKEN,
    )


vector_store = get_vectorstore()


def load_upload(vectorstore: AstraDBVectorStore | None = None) -> AstraDBVectorStore:
    vector_store_instance = vectorstore or vector_store
    example_pairs = [
        ("question", "question.html"),
        ("question.html", "server.js"),
        ("question.html", "server.py"),
        ("question.html", "solution.html"),
    ]
    all_docs = []
    for inp, out in example_pairs:
        all_docs.extend(
            QuestionModuleDocumentLoader(input_col=inp, output_col=out).load()
        )
    vector_store_instance.add_documents(all_docs)
    return vector_store_instance


if __name__ == "__main__":
    print("Adding question data to vectorstore")
    load_upload()
