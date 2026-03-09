# Lecture Processor

Lecture Processor extracts structured information from lecture PDFs using LLM-powered pipelines.

## What it does

- Generates a lecture summary (`lecture_analysis`)
- Extracts worked derivations (`extract_derivations`)
- Extracts in-lecture questions (`extract_question`)
- Generates conceptual review questions (`generate_questions`)
- Runs an end-to-end combined workflow (`full_extraction`)

Each workflow is implemented as a LangGraph pipeline and can save:

- `graph.png` (workflow visualization)
- `output.json` (structured model output)

## Requirements

- Python `>=3.11,<4.0`
- Poetry
- Access to Google GenAI (`gemini-2.5-flash`)
- LangSmith access for prompt pulls

## Setup

```bash
poetry install
```

Set environment variables (example):

```bash
GOOGLE_API_KEY=...
LANGSMITH_API_KEY=...
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=lecture-processor
```

## Run pipelines

From repository root:

```bash
poetry run python -m lecture_processor.lecture_analysis.graph
poetry run python -m lecture_processor.extract_derivations.graph
poetry run python -m lecture_processor.extract_question.graph
poetry run python -m lecture_processor.generate_questions.graph
poetry run python -m lecture_processor.full_extraction.graph
```

## Input PDF

Current scripts default to:

`data/Lecture_02_03.pdf`

Update the `pdf_path` in each `graph.py` if you want to process a different file.

## Output locations

- `src/lecture_processor/lecture_analysis/output/`
- `src/lecture_processor/extract_derivations/output/`
- `src/lecture_processor/extract_question/output/`
- `src/lecture_processor/generate_questions/output/`
- `src/lecture_processor/full_extraction/output/`
