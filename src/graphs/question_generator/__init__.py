from src.core.settings import get_settings


from langchain.chat_models import init_chat_model
from src.vectorstores.gestalt_question_vectorstore import vector_store

settings = get_settings()
model = init_chat_model(
    model=settings.model,
    model_provider=settings.model_provider,
)
