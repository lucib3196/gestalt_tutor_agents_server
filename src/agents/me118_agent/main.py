from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from langchain.agents import create_agent
from langsmith import Client

from src.settings import get_settings
from src.tools import refine_query
from src.utils import extract_langsmith_prompt
from src.agents.ME118Agent.vectorstore import vector_store
from src.agents.LibreText.main import retrieve_diffeq

settings = get_settings()
client = Client()

prompt = extract_langsmith_prompt(
    client.pull_prompt(
        "me118_tutor_prompt",
    )
)
print(prompt)


model = init_chat_model(
    model=settings.model,
    model_provider="google_genai",
)


@tool(response_format="content_and_artifact")
def retrieve_me118_lecture(query: str):
    """Retrieve information to help answer a query. Use the tool refine query before calling this tool"""
    retrieved_docs = vector_store.similarity_search(query, k=2)
    serialized = "\n\n".join(
        (f"Source: {doc.metadata}\nContent: {doc.page_content}")
        for doc in retrieved_docs
    )
    return serialized, retrieved_docs


tools = [retrieve_me118_lecture, refine_query, retrieve_diffeq]


agent = create_agent(model, tools, system_prompt=prompt)
