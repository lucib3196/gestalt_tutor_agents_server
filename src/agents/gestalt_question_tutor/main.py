from langchain.chat_models import init_chat_model
from langsmith import Client
from langchain.agents import create_agent

from src.settings import get_settings
from src.utils import extract_langsmith_prompt


settings = get_settings()
client = Client()
prompt = extract_langsmith_prompt(
    client.pull_prompt(
        "gestalt_question_tutor",
    )
)
model = init_chat_model(
    model=settings.model,
    model_provider="google_genai",
)


agent = create_agent(model, system_prompt=prompt)
