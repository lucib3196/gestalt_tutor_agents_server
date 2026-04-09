from src.core.settings import get_settings
from langchain_astradb import AstraDBVectorStore
from langchain.chat_models import init_chat_model

from langchain_google_genai import GoogleGenerativeAIEmbeddings

settings = get_settings()
embeddings = GoogleGenerativeAIEmbeddings(model=settings.embedding_model)
vector_store = AstraDBVectorStore(
    collection_name="gestalt_module",
    embedding=embeddings,
    api_endpoint=settings.ASTRA_DB_API_ENDPOINT,
    token=settings.ASTRA_DB_APPLICATION_TOKEN,
)


model = init_chat_model(
    model=settings.model,
    model_provider=settings.model_provider,
)
