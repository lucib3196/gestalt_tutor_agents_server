from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from langchain.agents import create_agent
from langsmith import Client

from src.settings import get_settings
from src.utils import extract_langsmith_prompt
from src.agents.ME135Agent.vectorstore import vector_store
from src.tools import refine_query


settings = get_settings()
client = Client()
prompt = extract_langsmith_prompt(
    client.pull_prompt(
        "me135_tutor_prompt",
    )
)

model = init_chat_model(
    model="gemini-2.0-flash",
    model_provider="google_genai",
)


@tool(response_format="content_and_artifact")
def retrieve_me135_lecture(query: str):
    """Retrieve information to help answer a query.before calling this call the refine_query tool"""
    retrieved_docs = vector_store.similarity_search(query, k=2)
    serialized = "\n\n".join(
        (f"Source: {doc.metadata}\nContent: {doc.page_content}")
        for doc in retrieved_docs
    )
    return serialized, retrieved_docs


tools = [retrieve_me135_lecture, refine_query]


agent = create_agent(model, tools, system_prompt=prompt)


if __name__ == "__main__":
    print(prompt)
