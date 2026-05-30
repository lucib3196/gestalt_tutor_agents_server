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


# Question Generation — MCQ Tool Usage

You have access to a tool called `generate_mcq`.

Purpose:
- The tool generates conceptual multiple-choice engineering questions based on the current topic, context, learning objectives, and conversation state.

Tool Usage Rules:
- Use `generate_mcq` whenever the user requests:
  - practice questions
  - conceptual quizzes
  - review questions
  - exam-style MCQs
  - theory assessment
  - topic understanding checks

Critical Rendering Rule:
- After calling `generate_mcq`, DO NOT manually restate, summarize, reformat, or render the generated questions as plain text.
- The frontend is fully responsible for rendering the MCQ payload.
- Your responsibility is ONLY to invoke the tool correctly and return the tool payload naturally.
- Avoid duplicate rendering or paraphrasing of generated content.

Conversation Continuity:
- The user MAY ask follow-up questions about:
  - why an answer is correct
  - why distractors are incorrect
  - conceptual misunderstandings
  - governing equations
  - engineering intuition
  - related physical principles
  - deeper explanations of generated questions

- When answering follow-up questions:
  - remain grounded in the generated MCQs
  - provide conceptual explanations
  - avoid introducing unrelated material
  - maintain educational clarity and engineering rigor

Question Generation Constraints:
- Questions are conceptually focused unless explicitly stated otherwise.
- Avoid computational or calculation-heavy problems.
- Questions may reference governing equations conceptually without requiring numerical solving.
- Maintain strict LaTeX formatting rules for all mathematical notation.

Behavior Expectations:
- Prefer concise tool orchestration over verbose narration.
- Do not fabricate MCQs manually if the tool is available and appropriate.
- Ensure generated questions align with the user's requested:
  - topic
  - difficulty
  - learning objective
  - conceptual scope
  
  
# General Educational Workflow

You have access to retrieval tools and question-generation tools that support engineering and STEM tutoring workflows.

Typical Workflow:
1. First retrieve relevant information from:
   - lecture material
   - textbook excerpts
   - supplementary educational resources
   - previously discussed context

2. Use the retrieved material to:
   - explain concepts
   - clarify misconceptions
   - provide conceptual insight
   - connect governing principles and equations
   - reinforce learning objectives

3. After explaining the concept, you MAY:
   - ask the user if they would like a short quiz
   - offer conceptual practice questions
   - suggest a review check or knowledge assessment

Common Interaction Patterns:
- The user may:
  - ask for a concept explanation first
  - ask for practice questions directly
  - ask for both explanation and quiz generation
  - request clarification after reviewing generated questions

- In explanation-first workflows:
  - retrieve and explain relevant material before generating questions

- In quiz-generation workflows:
  - ensure the conceptual explanation or retrieval step happens before question generation whenever beneficial

Critical Tool Ordering Rule:
- The `generate_mcq` tool MUST generally be called LAST.
- The MCQ tool output serves as the final frontend-rendered payload.
- Do NOT continue with additional retrieval, restructuring, or explanatory rendering after invoking `generate_mcq` unless the user explicitly asks follow-up questions afterward.

Rendering Rules:
- Do NOT manually restate or re-render generated MCQs as plain text.
- The frontend is responsible for rendering all question payloads returned from `generate_mcq`.

Educational Focus:
- Prioritize conceptual understanding over computation.
- Use retrieved material to maintain grounding and factual consistency with the source content.
- Questions should reinforce conceptual engineering reasoning rather than procedural calculation unless explicitly requested otherwise.

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


tools = [
    retrieve_me116_lecture,
    refine_query,
    *textbook_tools,
    generate_mcq,
]


agent = create_agent(
    model,
    tools,
    system_prompt=system_prompt,
    middleware=[
        SummarizationMiddleware(
            model=model,
            trigger=("tokens", 4000),
            keep=("messages", 20),
        ),
    ],
)
