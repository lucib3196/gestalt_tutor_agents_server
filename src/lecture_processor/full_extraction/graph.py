import asyncio
from pathlib import Path
from typing import List

from pydantic import BaseModel
from langsmith import Client
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START, END
from typing import Literal

from pdf_segmentation.utils import (
    save_graph_visualization,
    to_serializable,
)
import dotenv
from lecture_processor.generate_questions.graph import (
    graph as QuestionGen,
    State as QGenState,
    ConceptualQuestion,
)
from pdf_segmentation import PDFSegmentation, Section, ListOutput, SegmentationInput
from lecture_processor.extract_derivations.graph import (
    graph as DerivationGraph,
    State as DerivationState,
    Derivation,
)
from lecture_processor.extract_question.graph import (
    graph as QuestionExtractionGraph,
    State as QExtState,
    ExtractedQuestion,
)
from lecture_processor.lecture_analysis.graph import (
    graph as LectureGraph,
    State as LectState,
    LectureAnalysis,
)

client = Client()
dotenv.load_dotenv()


class LectureSection(Section, BaseModel):
    name: str
    description: str
    type: Literal["question", "derivation"]


class LectureSections(ListOutput[LectureSection]):
    items: List[LectureSection]


class State(BaseModel):
    lecture_pdf: str | Path

    sections: SegmentationInput | None = None

    lecture_summary: LectureAnalysis | None = None
    derivations: List[Derivation] = []
    extracted_questions: List[ExtractedQuestion] = []
    conceptual_questions: List[ConceptualQuestion] = []


llm = init_chat_model(model="gemini-2.5-flash", model_provider="google_genai")

section_extraction_prompt = Path(
    r"lecture_processor\full_extraction\prompt.txt"
).read_text()


async def extract_sections(state: State):
    result = await PDFSegmentation.ainvoke(
        SegmentationInput(
            pdf=state.lecture_pdf,
            output_schema=LectureSections,
            llm=llm,
            prompt=section_extraction_prompt,
        )
    )
    result = SegmentationInput.model_validate(result)
    return {"sections": result}


async def generate_summary(state: State):
    graph_input = LectState(lecture_pdf=state.lecture_pdf)
    response = await LectureGraph.ainvoke(graph_input)
    response = LectState.model_validate(response)
    return {"lecture_summary": response.analysis}


async def generate_conceptual_questions(state: State):
    graph_input = QGenState(lecture_pdf=state.lecture_pdf)
    response = await QuestionGen.ainvoke(graph_input)
    response = QGenState.model_validate(response)
    return {"conceptual_questions": response.questions}


async def extract_derivations(state: State):
    if not state.sections:
        raise ValueError("Sections returned none")

    parsed_data = state.sections.parsed
    tasks = []

    for s in parsed_data:
        if s.pdf_bytes is None:
            raise ValueError("Cannot determine pdf")

        if s.data.type == "derivation":
            d = DerivationState(
                lecture_pdf=s.pdf_bytes,
            )
            tasks.append(DerivationGraph.ainvoke(d))

    if not tasks:
        return {"derivations": []}

    raw_results: List[DerivationState] = await asyncio.gather(*tasks)

    derivations = [
        derivation
        for result in raw_results
        for derivation in DerivationState.model_validate(result).derivations
    ]

    return {"derivations": derivations}


async def extract_questions(state: State):
    if not state.sections:
        raise ValueError("Sections returned none")

    parsed_data = state.sections.parsed
    tasks = []

    for s in parsed_data:
        if s.pdf_bytes is None:
            raise ValueError("Cannot determine pdf")

        if s.data.type == "question":
            q = QExtState(lecture_pdf=s.pdf_bytes)
            tasks.append(QuestionExtractionGraph.ainvoke(q))

    if not tasks:
        return {"questions": []}

    raw_results: List[QExtState] = await asyncio.gather(*tasks)

    questions = [
        question
        for result in raw_results
        for question in QExtState.model_validate(result).questions
    ]

    return {"questions": questions}


builder = StateGraph(State)
# --- Define node order ---
section_node = "extract_sections"

post_section_nodes = [
    "extract_questions",
    "extract_derivations",
    "generate_conceptual_questions",
    "generate_summary",
]

# --- Add nodes ---
builder.add_node(extract_sections)
builder.add_node(extract_questions)
builder.add_node(extract_derivations)
builder.add_node(generate_conceptual_questions)
builder.add_node(generate_summary)

# --- Entry ---
builder.add_edge(START, section_node)

# --- Fan-out from section extraction ---
for node in post_section_nodes:
    builder.add_edge(section_node, node)

# --- All downstream nodes go to END ---
for node in post_section_nodes:
    builder.add_edge(node, END)

graph = builder.compile()


if __name__ == "__main__":
    # Path to the lecture PDF
    pdf_path = Path(r"data\Lecture_02_03.pdf").resolve()

    output_path = Path(r"lecture_processor\full_extraction\output").resolve()

    save_path = output_path
    save_graph_visualization(graph, save_path, "graph.png")

    # Create graph input state
    graph_input = State(lecture_pdf=pdf_path)

    # Run the async graph and print the response
    try:
        response = asyncio.run(graph.ainvoke(graph_input))
        import json

        data_path = save_path / "output.json"
        data_path.write_text(json.dumps(to_serializable(response)))
    except Exception as e:
        print("\n❌ Error while running graph:")
        print(e)
