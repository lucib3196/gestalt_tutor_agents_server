from lecture_processor.full_extraction.graph import graph as FullExtractionGraph, State
from pathlib import Path
import asyncio
import json
from pdf_segmentation.utils import to_serializable


async def process_single_lecture(
    pdf_path: Path,
    save_root: Path,
):
    """
    Run the FullExtractionGraph for a single PDF and save structured output.
    """
    filename = pdf_path.stem
    graph_input = State(lecture_pdf=pdf_path)
    try:
        response = await FullExtractionGraph.ainvoke(graph_input)
        print(f"\n--- Processing ({filename}) ---")
        # Create output directory
        output_dir = save_root / filename
        output_dir.mkdir(parents=True, exist_ok=True)
        # Save JSON output
        data_path = output_dir / "output.json"
        data_path.write_text(
            json.dumps(to_serializable(response), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return response
    except Exception as e:
        print(f"\n❌ Error while processing {filename}:")
        print(e)
        return None


async def batch_process(pdf_dir: str):
    path = Path(pdf_dir).resolve()
    if not path.exists():
        raise ValueError(f"Pdf path {path} does not exist")
    save_root = path / "output"
    save_root.mkdir(exist_ok=True)

    pdf_files = [
        p for p in path.iterdir() if p.is_file() and p.suffix.lower() == ".pdf"
    ]
    tasks = [process_single_lecture(pdf, save_root) for pdf in pdf_files]
    results = await asyncio.gather(*tasks)


if __name__ == "__main__":
    pdf_dir = r"data\me118"
    asyncio.run(batch_process(pdf_dir))
