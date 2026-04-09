from datetime import date, datetime, time
from pathlib import Path
from typing import Any
from uuid import UUID

from langgraph.graph.state import CompiledStateGraph
from pydantic import BaseModel


def to_serializable(obj: Any) -> Any:
    """Convert supported objects into JSON-serializable Python values."""
    if isinstance(obj, BaseModel):
        return obj.model_dump()
    if isinstance(obj, dict):
        return {key: to_serializable(value) for key, value in obj.items()}
    if isinstance(obj, list):
        return [to_serializable(value) for value in obj]
    if isinstance(obj, (datetime, date, time)):
        return obj.isoformat()
    if isinstance(obj, UUID):
        return str(obj)
    if isinstance(obj, Path):
        return obj.as_posix()
    return obj


def write_image_data(image_bytes: bytes, folder_path: str | Path, filename: str) -> str:
    """Write PNG image bytes to disk and return the saved path."""
    try:
        path = Path(folder_path).resolve()
        path.mkdir(exist_ok=True)
        save_path = path / filename

        if save_path.suffix != ".png":
            raise ValueError(
                "Suffix allowed is only PNG either missing or nnot allowed"
            )
        save_path.write_bytes(image_bytes)
        return save_path.as_posix()
    except Exception as error:
        raise ValueError(f"Could not save image {error}") from error


def save_graph_visualization(
    graph: CompiledStateGraph | Any,
    folder_path: str | Path,
    filename: str,
) -> None:
    """Render a graph visualization to PNG and save it to disk."""
    try:
        image_bytes = graph.get_graph().draw_mermaid_png()
        save_path = write_image_data(image_bytes, folder_path, filename)

        print(f"Saved graph visualization at: {save_path}")
    except ValueError:
        raise
    except Exception as error:
        print(f"Graph visualization failed: {error}")
