from langchain_astradb import AstraDBVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os
from settings import get_settings

settings = get_settings()


embeddings = GoogleGenerativeAIEmbeddings(model=settings.embedding_model)
try:
    vs = AstraDBVectorStore(
        collection_name="math_2562_libretext_diff_eq_with_linear_algebra",
        embedding=embeddings,
        api_endpoint=os.getenv("ASTRA_DB_API_ENDPOINT"),
        token=os.getenv("ASTRA_DB_APPLICATION_TOKEN"),
    )
    assert vs
except Exception as e:
    raise ValueError(f"Failed to load vectorstore {e}")

if __name__ == "__main__":
    print("Loading vectorstore")
    result = vs.similarity_search("What is differential equations")
    print(result)
