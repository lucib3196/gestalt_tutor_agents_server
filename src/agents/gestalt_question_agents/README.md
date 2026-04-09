# Gestalt Question Agents

This folder contains two agent implementations for generating Gestalt question content.

## Files

- `agent_module.py` packages everything together into a single Gestalt module workflow. Use this when you want one agent path that produces the full bundled module output.
- `agent_simple.py` provides a more modular version of the same idea. Its tools are separated out, making it easier to work with the generation flow in smaller pieces.

## Related Prompts

To better understand how each agent is intended to behave, read the prompt files below:

- `src/prompts/gestalt_module_prompt.md`
- `src/prompts/gestalt_agent_simple.md`
