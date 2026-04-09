
# Gestalt Agent Server

A LangGraph-powered backend server hosting Gestalt AI agents (ME135, ME118,Question Generator, etc.).

---

# Installation Guide

## Clone the Repository

```bash
git clone https://github.com/lucib3196/gestalt_tutor_agents_server.git
cd gestalt_tutor_agents_server
```

---

## Install Dependencies (Poetry)

Make sure you have Poetry installed:

```bash
pip install poetry
```

Then install project dependencies:

```bash
poetry install
```

Activate the virtual environment:

```bash
poetry shell
```

---

# Environment Configuration

Create a `.env` file in the root of the project.

A template is provided — copy it:

```bash
cp .env.example .env
```

Then configure your keys.

---

##  Example `.env` Template

```env
# Gemini Settings
GOOGLE_API_KEY=
MODEL= 
EMBEDDING_MODEL=

# Langsmith config
LANGSMITH_TRACING=
LANGSMITH_ENDPOINT=
LANGSMITH_API_KEY=
LANGSMITH_PROJECT="GestaltMETutor"
# Vectorstor
ASTRA_DB_API_ENDPOINT=
ASTRA_DB_APPLICATION_TOKEN=

STORAGE_BUCKET=
FIREBASE_CRED=
FIREBASE_AUTH_EMULATOR_HOST=127.0.0.1:9099
STORAGE_EMULATOR_HOST=http://localhost:9199
```

---

## What Each Section Does

### Gemini Settings

* `GOOGLE_API_KEY` → Required for Gemini models
* `MODEL` → Main LLM model (e.g. `gemini-1.5-pro`)
* `EMBEDDING_MODEL` → Embedding model for vector search

---

### LangSmith

* Enables tracing and debugging of agent runs
* Required for production observability

---

### AstraDB

* Vector database for RAG retrieval
* Required for lecture-grounded tutoring

---

# Project Structure

```
gestalt-agent-server/
│
├── src/
│   ├── agents/        # Defined LangGraph agents
│   │    ├── ME135Agent/
│   │    ├── ME118Agent/
│   │    └── ...
│   │
│   ├── tools/
│   ├── settings.py
│   └── utils/
│
├── .env
├── pyproject.toml
└── README.md
```

---

# Running the Server (Development Mode)

To run the full LangGraph development server:
from root dir

```bash
langgraph dev
```

This will:

* Start the local LangGraph server
* Load all defined agents inside `src/agents`
* Expose them for testing and UI integration

By default it runs on:

```
http://127.0.0.1:2024
```

---

#  Notes

* Ensure your `.env` file is configured before running.
* If environment variables are not detected, confirm your `settings.py` loads `.env`.
* For production deployment, you must provide secure API keys and disable debug tracing.

---

#  Development Workflow

* Add or modify agents inside `langgraph.json`
* Restart `langgraph dev`
---
