import asyncio
from pathlib import Path
from typing import List


from pydantic import BaseModel
from langsmith import Client
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START, END

from pdf_invoke import MultiModalLLM
from pdf_segmentation.utils import (
    save_graph_visualization,
    to_serializable,
)

from .model import Derivation
from lecture_processor.utils import extract_langsmith_prompt


client = Client()

prompt = extract_langsmith_prompt(client.pull_prompt("extract-derivations"))

llm = init_chat_model(model="gemini-2.5-flash", model_provider="google_genai")


class State(BaseModel):
    lecture_pdf: str | Path | bytes
    derivations: List[Derivation] = []


class Response(BaseModel):
    derivations: List[Derivation]


async def extract_derivations(state: State):
    processor = MultiModalLLM(prompt=prompt, model=llm)

    response = await processor.ainvoke(
        pdf=state.lecture_pdf,
        output_model=Response,
    )
    response = Response.model_validate(response)
    return {"derivations": response.derivations}


builder = StateGraph(State)
builder.add_node("extract_derivations", extract_derivations)

builder.add_edge(START, "extract_derivations")

builder.add_edge("extract_derivations", END)

graph = builder.compile()


if __name__ == "__main__":
    # Path to the lecture PDF
    pdf_path = Path(r"data\Lecture_02_03.pdf").resolve()

    output_path = Path(r"lecture_processor\extract_derivations\output").resolve()

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
