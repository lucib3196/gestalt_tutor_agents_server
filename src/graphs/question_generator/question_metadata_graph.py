import json
from pathlib import Path
from typing import List
from pydantic import BaseModel, Field
from langgraph.graph import END, START, StateGraph
from pydantic import Field
from src.graphs import (
    Question,
    QuestionTypes,
    save_graph_visualization,
    to_serializable,
)
from .initialization import model
from src.prompts.load_prompts import resolve_prompt
from langsmith import Client


client = Client()
base_prompt = resolve_prompt("question_metadata_graph_prompt")


class QuestionMetaData(BaseModel):
    title: str = Field(..., description="A concise title summarizing the question")
    qTypes: List[QuestionTypes] = []
    topics: List[str] = Field(default=[])
    isAdaptive: bool


class State(BaseModel):
    question: Question
    metadata: QuestionMetaData | None = Field(
        default=None,
        description="The metadata to generate",
    )
    isAdaptive: bool | None = Field(
        default=None,
        description="Whether the question is adaptive or not. If the None is passed it will auto generate during metadata generation. ",
    )


def generate_question_metadata(state: State):
    question_text = state.question.question_text

    structured_model = model.with_structured_output(QuestionMetaData)
    prompt = f"""
    {base_prompt}
    Question {question_text}
    """

    result = structured_model.invoke(prompt)
    metadata = QuestionMetaData.model_validate(result)

    # Override
    if state.isAdaptive is not None:
        metadata.isAdaptive = state.isAdaptive

    return {"metadata": metadata}


workflow = StateGraph(State)
# Define Nodes
workflow.add_node("generate_question_metadata", generate_question_metadata)
# Connect
workflow.add_edge(START, "generate_question_metadata")
workflow.add_edge("generate_question_metadata", END)

# memory = MemorySaver()
# app = workflow.compile(checkpointer=memory)
app = workflow.compile()
if __name__ == "__main__":
    config = {"configurable": {"thread_id": "customer_123"}}
    question = Question(
        question_text="A car is traveling along a straight rode at a constant speed of 100mph for 5 hours calculate the total distance traveled",
        solution_guide=None,
        final_answer=None,
        question_html="",
    )
    input_state: State = State(**{"question": question, "metadata": None})
    result = app.invoke(input_state, config=config)  # type: ignore
    print(result["metadata"])

    # Save output
    output_path = Path(
        r"src/graphs/outputs/metadata_graph"
    )
    save_graph_visualization(app, output_path, filename="graph.png")
    data_path = output_path / "output.json"
    data_path.write_text(json.dumps(to_serializable(result)))
