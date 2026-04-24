from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from langsmith import Client
from src.agents.multi_textbook_agent.main import (
    AGENT_SYSTEM_PROMPT as TEXTBOOK_TOOL_PROMPT,
    textbook_tools,
)
from src.agents.diff_libretext.main import retrieve_diffeq
from src.agents.me118_agent.vectorstore import vector_store
from src.core.settings import get_settings
from src.prompts.load_prompts import (
    extract_langsmith_prompt,
    load_local_prompt,
)

from src.tools import refine_query

settings = get_settings()
client = Client()

prompt_base_name = "me116_tutor_prompt"
if settings.prompt_source == "local":
    prompt = load_local_prompt(f"src/prompts/{prompt_base_name}")
else:
    prompt = extract_langsmith_prompt(client.pull_prompt(prompt_base_name))

system_prompt = f"""
{prompt}

Textbook Instructions
{TEXTBOOK_TOOL_PROMPT}
"""


model = init_chat_model(
    model=settings.model,
    model_provider="google_genai",
)


@tool(response_format="content_and_artifact")
def retrieve_me116_lecture(query: str):
    """Retrieve information to help answer a query. Use the tool refine query before calling this tool"""
    retrieved_docs = vector_store.similarity_search(query, k=3)
    serialized = "\n\n".join(
        (f"Source: {doc.metadata}\nContent: {doc.page_content}")
        for doc in retrieved_docs
    )
    return serialized, retrieved_docs


tools = [retrieve_me116_lecture, refine_query, retrieve_diffeq, *textbook_tools]


agent = create_agent(model, tools, system_prompt=prompt)
