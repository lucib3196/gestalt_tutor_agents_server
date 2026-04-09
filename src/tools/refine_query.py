from typing import List, Literal

from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from pydantic import BaseModel

from src.core.settings import get_settings


settings = get_settings()

model = init_chat_model(
    model=settings.model,
    model_provider="google_genai",
)


class ImproveSearchQuery(BaseModel):
    user_request: str
    user_intent: Literal[
        "derivation_explanation",
        "concept_review",
        "practice_problem",
        "definition",
    ]
    queries: int = 3


class RefinedQuery(BaseModel):
    queries: List[str]


SYSTEM_PROMPT = """
You are a retrieval optimization assistant for an engineering tutoring system.

Your task is to convert a student request into optimized database search queries.

Generate exactly {num_queries} distinct search queries.

Guidelines:
- Expand technical terminology.
- Include relevant mechanical engineering vocabulary.
- Avoid vague wording.
- Keep each query concise but information-dense.

Intent-specific rules:
- derivation_explanation → emphasize derivation steps, mathematical justification, assumptions
- concept_review → emphasize governing equations, definitions, physical interpretation
- practice_problem → emphasize worked examples, applications, numerical solutions
- definition → emphasize formal definition and mathematical expression

Return only structured output.
"""


@tool(args_schema=ImproveSearchQuery)
def refine_query(
    user_request: str,
    user_intent: str = "concept_review",
    queries: int = 3,
) -> List[str]:
    """Refine a user request into optimized search queries for lecture retrieval. After using this tool use the available search tools to look throught the database of notes"""

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            (
                "human",
                "User Request: {user_request}\nIntent: {user_intent}",
            ),
        ]
    )

    llm = model.with_structured_output(RefinedQuery)

    chain = prompt.partial(num_queries=queries) | llm

    response = chain.invoke(
        {
            "user_request": user_request,
            "user_intent": user_intent,
        }
    )

    return RefinedQuery.model_validate(response).queries
