# Prompts

This folder is for keeping saved prompt files available locally when we need them. The
`load_prompts.py` module pulls prompt content from LangSmith, writes it into
`src/prompts`, and provides helpers to read those saved prompts back into the app.

Quick overview of the functions in `load_prompts.py`:

- `fetch_all_prompts()` downloads each prompt listed in `VALID_PROMPTS`, extracts the
  prompt text, and saves it as a local `.txt` file in this folder.
- `load_local_prompt(prompt_name)` reads one of the saved local prompt files so it can
  be used in the app without pulling it again.
- `extract_langsmith_prompt(base)` takes a LangSmith prompt object and extracts the
  system prompt text that gets saved locally.

This is mainly useful for local testing, inspection, and keeping prompt content nearby
when a saved prompt is needed.
