from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from langsmith import Client
from src.agents.multi_textbook_agent.main import (
    AGENT_SYSTEM_PROMPT as TEXTBOOK_TOOL_PROMPT,
    textbook_tools,
)
from langchain.agents.middleware import SummarizationMiddleware

from src.agents.diff_libretext.main import retrieve_diffeq
from src.agents.me116_agent.vectorstore import vector_store
from src.core.settings import get_settings
from src.prompts.load_prompts import (
    extract_langsmith_prompt,
    load_local_prompt,
)
from typing import Optional

from src.tools import refine_query
from src.tools.generate_questions import generate_mcq

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
    model="gemini-3.1-flash-lite",
    model_provider="google_genai",
)


@tool(response_format="content_and_artifact")
def retrieve_me116_lecture(query: str):
    """Search ME116 lecture notes for course-specific concepts, examples, and explanations.

    Use this after refining the student's question with refine_query, especially when the
    answer should come from ME116 lecture material rather than the textbook or homework.
    """
    retrieved_docs = vector_store.similarity_search(query, k=3)
    serialized = "\n\n".join(
        (f"Source: {doc.metadata}\nContent: {doc.page_content}")
        for doc in retrieved_docs
    )
    return serialized, retrieved_docs


@tool(response_format="content_and_artifact")
def retrieve_me116_homework(query: str, homework_set: Optional[int] = None):
    """Search ME116 homework solutions for worked examples and solution guidance.

    Use this after refining the student's question with refine_query when the student asks
    about a homework problem, solution method, calculation steps, or expected result.

    Args:
        query: The refined search query describing the concept, problem, or solution step
            to look up in the ME116 homework solution corpus.
        homework_set: Optional homework number to restrict the search to a specific
            assignment, such as 1 for "homework 1". Leave as None when the student does
            not identify a particular homework set.
    """
    filter_metadata = {"type": "homework_solution"}
    if homework_set is not None:
        filter_metadata["homework"] = str(homework_set)

    retrieved_docs = vector_store.similarity_search(query, k=5, filter=filter_metadata)
    serialized = "\n\n".join(
        (f"Source: {doc.metadata}\nContent: {doc.page_content}")
        for doc in retrieved_docs
    )
    return serialized, retrieved_docs


tools = [
    retrieve_me116_lecture,
    refine_query,
    *textbook_tools,
    generate_mcq,
    retrieve_me116_homework,
]


agent = create_agent(
    model,
    tools,
    system_prompt=system_prompt,
    middleware=[],
)
