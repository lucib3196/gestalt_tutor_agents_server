import hashlib
from typing import List, Literal, Union, Tuple

from pydantic import BaseModel
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain.agents import create_agent

from agents.LibreText.vectorstore import vs
from settings import get_settings

settings = get_settings()

# -----------------------
# LLM (used for refine_query)
# -----------------------
model = init_chat_model(
    model=settings.model,
    model_provider="google_genai",
)


# -----------------------
# Your existing refine_query tool
# -----------------------
class ImproveSearchQuery(BaseModel):
    user_request: str
    user_intent: Literal[
        "solve_ode",
        "method_selection",
        "concept_review",
        "definition",
        "practice_problem",
        "initial_value_problem",
    ]
    queries: int = 3


class RefinedQuery(BaseModel):
    queries: List[str]


REFINE_QUERY_PROMPT = """
You are a retrieval optimization assistant for a differential equations tutoring system.

Convert a student request into optimized database search queries for textbook/lecture retrieval.

Generate exactly {num_queries} distinct search queries.

Guidelines:
- Expand mathematical and technical terminology.
- Include ODE method keywords (separable, linear, exact, integrating factor, Bernoulli, homogeneous,
  characteristic equation, undetermined coefficients, variation of parameters, Laplace transform, series solutions).
- Include problem structure keywords when relevant (IVP/IC, boundary value, order, linear/nonlinear).
- Avoid vague wording.
- Keep each query concise but information-dense.

Intent-specific rules:
- solve_ode → emphasize “worked example”, “step-by-step solution”, “method + solution form”
- method_selection → emphasize “how to choose method”, “classification”, “decision rules”
- concept_review → emphasize “definition”, “interpretation”, “common mistakes”
- definition → emphasize “formal definition” + “mathematical expression”
- practice_problem → emphasize “practice problems” + “solutions” + “similar examples”
- initial_value_problem → emphasize “IVP”, “initial condition”, “apply IC”, “solve for constant”

Return only structured output.
"""


@tool(args_schema=ImproveSearchQuery)
def refine_query(
    user_request: str,
    user_intent: str = "concept_review",
    queries: int = 3,
) -> List[str]:
    """Generate multiple optimized search queries from a student request.
    After using this tool, call retrieve_diffeq with the returned list of queries.
    """

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", REFINE_QUERY_PROMPT),
            ("human", "User Request: {user_request}\nIntent: {user_intent}"),
        ]
    )

    llm = model.with_structured_output(RefinedQuery)
    chain = prompt.partial(num_queries=queries) | llm

    response = chain.invoke({"user_request": user_request, "user_intent": user_intent})

    rq = RefinedQuery.model_validate(response)
    qs = rq.queries[:queries]
    if len(qs) < queries:
        qs += [user_request] * (queries - len(qs))
    return qs


class RetrieveInput(BaseModel):
    query: Union[str, List[str]]
    k: int = 8  # default top-k returned to the model


# Helper function for deduplication based on source + content hash
def _doc_key(doc) -> str:
    source = str(doc.metadata.get("source", ""))
    content_hash = hashlib.md5(doc.page_content.encode("utf-8")).hexdigest()
    return f"{source}::{content_hash}"


# Helper funtion purely for formatting the retrieved docs into a single string for the agent to read
def _serialize_docs(docs) -> str:
    parts = []
    for i, doc in enumerate(docs, start=1):
        source = doc.metadata.get("source", "")
        title = doc.metadata.get("title") or doc.metadata.get("section") or ""
        header = f"[EXCERPT {i}]"
        if title:
            header += f" {title}"
        parts.append(f"{header}\nSOURCE: {source}\n\n{doc.page_content.strip()}")
    return "\n\n---\n\n".join(parts)


@tool(args_schema=RetrieveInput, response_format="content_and_artifact")
def retrieve_diffeq(
    query: Union[str, List[str]], k: int = 8
) -> Tuple[str, List]:  # Probably should lower k for faster response times
    """Retrieve relevant excerpts from the diffeq database.
    Accepts a single query string, or a list of refined queries (recommended).
    Returns (serialized_text, docs_artifact).
    """

    queries = query if isinstance(query, list) else [query]

    merged = []
    seen = set()

    per_query_k = max(2, min(4, k))

    for q in queries:
        docs = vs.similarity_search(q, k=per_query_k)
        for d in docs:
            key = _doc_key(d)
            if key in seen:
                continue
            seen.add(key)
            merged.append(d)

    # If still short, backfill from the best query
    if merged and len(merged) < k:
        extra = vs.similarity_search(queries[0], k=k)
        for d in extra:
            key = _doc_key(d)
            if key not in seen:
                seen.add(key)
                merged.append(d)

    merged = merged[:k]
    return _serialize_docs(merged), merged


AGENT_SYSTEM_PROMPT = """
You are a patient differential equations tutor.

Tool workflow:
- If the request is broad/vague, call refine_query first (pick the best user_intent).
- Then call retrieve_diffeq using the list returned from refine_query.
- Use the retrieved excerpts to teach step-by-step.
- If the excerpts do not contain enough info, say what’s missing and ask 1-2 targeted follow-ups.
- Cite sources by listing SOURCE URLs you actually used.

Don’t invent citations or textbook content.
"""

tools = [refine_query, retrieve_diffeq]
agent = create_agent(model, tools=tools, system_prompt=AGENT_SYSTEM_PROMPT)
