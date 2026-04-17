import hashlib
from typing import List, Tuple, Union

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from pydantic import BaseModel

from src.core.settings import get_settings
from src.retrievers.textbook_retrievers import TEXTBOOKS, VALID_TEXTBOOK, init_vectorstores
from src.tools.refine_query import refine_query


settings = get_settings()
model = init_chat_model(
    model=settings.model,
    model_provider="google_genai",
)


class RetrieveInput(BaseModel):
    query: Union[str, List[str]]
    k: int = 6


def _doc_key(doc) -> str:
    source = str(doc.metadata.get("source", ""))
    content_hash = hashlib.md5(doc.page_content.encode("utf-8")).hexdigest()
    return f"{source}::{content_hash}"


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


vectorstores = init_vectorstores()


def _build_retriever_tool(textbook_key: VALID_TEXTBOOK):
    tb = TEXTBOOKS[textbook_key]
    vs = vectorstores[textbook_key]
    tool_name = f"retrieve_{tb.key}"

    def _retrieve(query: Union[str, List[str]], k: int = 6) -> Tuple[str, List]:
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

        if merged and len(merged) < k:
            extra = vs.similarity_search(queries[0], k=k)
            for d in extra:
                key = _doc_key(d)
                if key not in seen:
                    seen.add(key)
                    merged.append(d)

        merged = merged[:k]
        return _serialize_docs(merged), merged

    _retrieve.__name__ = tool_name
    _retrieve.__doc__ = (
        f"Retrieve relevant excerpts from {tb.key}. "
        f"When to call: {tb.description} "
        "Accepts one query or a list of refined queries. "
        "Returns (serialized_text, docs_artifact)."
    )

    return tool(args_schema=RetrieveInput, response_format="content_and_artifact")(
        _retrieve
    )


textbook_tools = [_build_retriever_tool(key) for key in TEXTBOOKS]
textbook_access = "\n".join(f"- {v.key}: {v.description}" for v in TEXTBOOKS.values())
tool_names = "\n".join(f"- retrieve_{v.key}" for v in TEXTBOOKS.values())

# TODO Update this prompt such that you always return the sources when available. Since they may be links format them appropriately. Also for ormatting in latext to delimit math using $ for inline and $$ for block levle math
AGENT_SYSTEM_PROMPT = f"""You are a patient STEM tutor.

You have retrieval access to these textbooks:
{textbook_access}

Available retrieval tools:
{tool_names}

Tool workflow:
- If the request is broad or vague, call refine_query first (pick the best user_intent).
- Then call the most relevant retrieval tool(s) with the refined query list.
- Use retrieved excerpts to teach step-by-step.
- If excerpts are insufficient, say what is missing and ask 1-2 targeted follow-ups.
- Cite sources by listing SOURCE URLs you actually used.
- Do not invent citations or textbook content.
"""

tools = [refine_query, *textbook_tools]
agent = create_agent(model, tools=tools, system_prompt=AGENT_SYSTEM_PROMPT)
