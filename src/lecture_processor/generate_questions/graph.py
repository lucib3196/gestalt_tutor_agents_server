import asyncio
from pathlib import Path
from typing import List

from pydantic import BaseModel, Field
from langsmith import Client
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START, END

from .model import ConceptualQuestion
from pdf_invoke import MultiModalLLM
from pdf_segmentation.utils import (
    save_graph_visualization,
    to_serializable,
)

client = Client()

llm = init_chat_model(model="gemini-2.5-flash", model_provider="google_genai")


class State(BaseModel):
    lecture_pdf: str | Path | bytes
    questions: List[ConceptualQuestion] = []


class Response(BaseModel):
    questions: List[ConceptualQuestion]


async def generate_questions(state: State):
    processor = MultiModalLLM(
        prompt="Based on the lecture material generate max of 3 conceptual questions based on the lecture material meant to test students at the end of the lecture",
        model=llm,
    )

    response = await processor.ainvoke(
        pdf=state.lecture_pdf,
        output_model=Response,
    )
    response = Response.model_validate(response)
    return {"questions": response.questions}


builder = StateGraph(State)
builder.add_node("generate_questions", generate_questions)

builder.add_edge(START, "generate_questions")

builder.add_edge("generate_questions", END)

graph = builder.compile()


if __name__ == "__main__":
    # Path to the lecture PDF
    pdf_path = Path(r"data\Lecture_02_03.pdf").resolve()
    output_path = Path(r"lecture_processor\generate_questions\output").resolve()

    save_path = output_path
    save_graph_visualization(graph, save_path, "graph.png")

    # Create graph input state
    graph_input = State(lecture_pdf=pdf_path)

    # Run the async graph and print the response
    try:
        response = asyncio.run(graph.ainvoke(graph_input))
        print("\n--- Graph Response ---")
        print(response)
        import json

        data_path = save_path / "output.json"
        data_path.write_text(json.dumps(to_serializable(response)))
    except Exception as e:
        print("\n❌ Error while running graph:")
        print(e)
