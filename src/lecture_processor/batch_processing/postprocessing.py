from pathlib import Path
import json
from lecture_processor.full_extraction.graph import State
import asyncio
from lecture_processor.models import (
    Derivation,
    ConceptualQuestion,
    LectureAnalysis,
    ExtractedQuestion,
)
import base64


async def postprocess_lecture_output(
    input_json_path: Path,
    output_text_path: Path,
) -> None:
    """
    Postprocess a lecture graph output JSON into a cleaned,
    human-readable text artifact.
    """

    # ----------------------------
    # Load JSON
    # ----------------------------
    content = json.loads(input_json_path.read_text(encoding="utf-8"))
    content.pop("llm", None)

    # ----------------------------
    # Validate and reconstruct models
    # ----------------------------
    lecture_pdf = content.get("lecture_pdf", "")

    lecture_analysis = LectureAnalysis.model_validate(
        content.get("lecture_summary", {})
    )

    derivations = [Derivation.model_validate(d) for d in content.get("derivations", [])]

    extracted_questions = [
        ExtractedQuestion.model_validate(q)
        for q in content.get("extracted_questions", [])
    ]

    conceptual_questions = [
        ConceptualQuestion.model_validate(q)
        for q in content.get("conceptual_questions", [])
    ]

    # ----------------------------
    # Convert to text
    # ----------------------------
    lecture_pdf_name = Path(lecture_pdf).name

    lecture_analysis_text = lecture_analysis.as_string()

    derivations_text = "".join(d.as_string() for d in derivations)

    questions_text = "".join(q.as_string() for q in extracted_questions)

    conceptual_text = "".join(q.as_string() for q in conceptual_questions)

    # ----------------------------
    # Assemble final output
    # ----------------------------
    final_text = (
        f"# Lecture Source: {lecture_pdf_name}\n\n"
        f"{lecture_analysis_text}\n\n"
        f"## Derivations\n\n"
        f"{derivations_text}\n\n"
        f"## Questions\n\n"
        f"{questions_text}\n\n"
        f"## Conceptual Questions\n\n"
        f"{conceptual_text}"
    )

    # ----------------------------
    # Write output
    # ----------------------------
    output_text_path.parent.mkdir(parents=True, exist_ok=True)
    output_text_path.write_text(final_text, encoding="utf-8")
    pdf_bytes = content.get("sections", {}).get("pdf_bytes")
    pdf = Path(output_text_path.parent / f"{lecture_pdf_name}").write_bytes(
        base64.b64decode(pdf_bytes)
    )


async def main():
    folder_path = Path(r"data\me118_update\outputs").resolve()

    filename = "output.json"
    tasks = []

    for p in folder_path.iterdir():
        if not p.is_dir():
            continue

        output_text_name = f"{p.name.split('.')[0]}.md"
        output = p / output_text_name
        data = p / filename

        tasks.append(
            postprocess_lecture_output(
                data,
                output_text_path=output,
            )
        )

    # Run all postprocessing concurrently
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
