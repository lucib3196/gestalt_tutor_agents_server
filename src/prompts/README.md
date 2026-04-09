# Prompts

This folder stores prompt files used by agents and graph generators. The
`load_prompts.py` module can fetch prompt templates from LangSmith, save them
locally, load local prompt files, and resolve a prompt from either the local
filesystem or LangSmith depending on `settings.prompt_source`.

## Current functions in `load_prompts.py`

- `fetch_all_prompts()`: Pulls every prompt listed in `VALID_PROMPTS` from
  LangSmith, extracts the prompt text, and writes each one to
  `src/prompts/<prompt_name>.md`.
- `load_local_prompt(prompt_name: str) -> str`: Reads a prompt file from the
  local `src/prompts` directory and returns its contents.
- `extract_langsmith_prompt(base: Any) -> str`: Extracts the system prompt text
  from a LangSmith `ChatPromptTemplate`.
- `resolve_prompt(prompt_identifier: str) -> str`: Returns a prompt by loading
  it locally when `prompt_source` is `local`, or by pulling and extracting it
  from LangSmith otherwise.

## Current prompt files

- `me118_tutor_prompt.md`: Defines a lecture-grounded ME118 tutor focused on
  engineering modeling and differential equations. It emphasizes retrieving
  course material first and teaching through assumptions, governing laws, and
  model interpretation.
- `me135_tutor_prompt.md`: Defines a lecture-grounded ME135 tutor for transport
  phenomena. It centers explanations on conservation laws, constitutive
  equations, and course-specific notation from the lecture notes.
- `question_html_graph_prompt.md`: Guides generation of a structured
  `question.html` file from a raw engineering problem. It focuses on clean HTML,
  parameterized values, PrairieLearn inputs, and strict LaTeX formatting rules.
- `server_js_graph_prompt.md`: Guides generation of a JavaScript `generate()`
  file for engineering questions. It focuses on randomized parameters,
  step-by-step calculations, and returning `params` plus `correct_answers`.
- `server_py_graph_prompt.md`: Guides generation of a Python `generate()`
  function for engineering questions. It mirrors the JavaScript prompt but
  targets Python syntax and a returned `data` dictionary.

This folder is mainly useful for local development, prompt inspection, and
keeping prompt content available without needing to pull it every time.
