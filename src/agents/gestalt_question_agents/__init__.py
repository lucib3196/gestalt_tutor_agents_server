from langchain.chat_models import init_chat_model

from src.core.settings import get_settings
from src.graphs.question_generator.question_metadata_graph import (
    QuestionMetaData,
    State as MetadataState,
    app as question_metadata_graph,
)
from src.graphs.question_generator.question_html_graph import (
    State as QState,
    app as question_html_tool,
)
from src.graphs.question_generator.solution_html_graph import (
    State as SolutionState,
    app as solution_html_tool,
)
from src.graphs.question_generator.server_js_graph import (
    State as JSState,
    app as server_js_tool,
)
from src.graphs.question_generator.server_py_graph import (
    State as PyState,
    app as server_py_generator,
)
from src.prompts.load_prompts import resolve_prompt
from src.tools.file_tools import prepare_zip

settings = get_settings()
model = init_chat_model(
    model=settings.model,
    model_provider=settings.model_provider,
)
