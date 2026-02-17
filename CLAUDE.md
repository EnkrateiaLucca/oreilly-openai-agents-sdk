# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

O'Reilly Live Training course teaching AI agent development with the OpenAI Agents SDK. The content is delivered through sequential Jupyter notebooks (00 through 05) plus a capstone project, with supporting assets and a presentation.

## Environment Setup

```bash
# Full setup (conda + deps + Jupyter kernel)
make all

# Or manually:
conda activate openai-agents-sdk
pip install openai-agents

# Update dependencies
make env-update
```

- Conda env name: `openai-agents-sdk` (Python 3.11)
- Dependency management: `uv` with pip-compile (`requirements/requirements.in` → `requirements.txt`)
- Requires `OPENAI_API_KEY` environment variable

## Repository Structure

- `notebooks/` — Core course content as Jupyter notebooks (numbered 00–05 for sequential progression)
  - 00: Agent loop fundamentals
  - 01: Agents and tools
  - 02: Structured output and context
  - 03: Multi-agent patterns (handoffs)
  - 04: Guardrails, sessions, tracing, MCP
  - 05: Capstone — customer service agent
- `assets/` — Diagrams, cheatsheets (PDF), and SDK documentation reference (`openai-agents-sdk-docs-llmstxt.txt`)
- `presentation/` — Course presentation materials
- `scripts/` — Standalone Python scripts (currently empty)
- `requirements/` — Dependency files managed via uv/pip-compile

## Key SDK Patterns Used

The notebooks use `openai-agents` SDK with these core imports:
- `from agents import Agent, Runner, function_tool` — agent creation and execution
- `Runner.run_sync()` for synchronous, `Runner.run()` for async, `Runner.run_streamed()` for streaming
- `from agents import InputGuardrail, OutputGuardrail` — input/output validation
- `from agents.extensions.models.litellm_model import LitellmModel` — non-OpenAI model providers
- MCP integration via `MCPServerStdio`, `MCPServerSse`, `MCPServerStreamableHttp`

## Development Notes

- All code runs in notebooks; there are no standalone `.py` modules to test
- When adding new notebooks, follow the numbered naming convention: `NN-description.ipynb`
- The SDK reference doc is available locally at `assets/openai-agents-sdk-docs-llmstxt.txt`
- Google API integrations (Sheets, Calendar, Gmail) require additional OAuth credentials
