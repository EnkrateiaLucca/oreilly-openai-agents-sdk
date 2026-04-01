# CLAUDE.md

Guidance for Claude Code when working on this repository.

## Project Overview

O'Reilly Live Training course: **Building AI Agents with OpenAI's Agents SDK**. Progressive Jupyter notebooks (00–05) teach agent fundamentals through a capstone, plus two standalone demo apps. SDK version: `openai-agents==0.13.3`. Primary model: `gpt-4.1`, secondary: `gpt-5-mini`.

## Environment

```bash
make all                    # Full setup: conda env + deps + Jupyter kernel
conda activate openai-agents-sdk
make env-update             # Recompile & sync deps
```

- **Python 3.11** via conda env `openai-agents-sdk`
- **Deps**: `uv` with pip-compile (`requirements/requirements.in` → `requirements.txt`)
- **Required env var**: `OPENAI_API_KEY`
- **Optional**: Google OAuth creds for Sheets/Calendar/Gmail integrations in notebook 04

## Repository Map

```
notebooks/                   # Core course content (run sequentially)
  00-agent-loop.ipynb        # Agent loop concept, single vs iterative execution
  01-agents-and-tools.ipynb  # Agent definitions, @function_tool decorator
  02-structured-output-and-context.ipynb  # Pydantic output models, RunContextWrapper
  03-multi-agent-patterns.ipynb          # Handoffs (decentralized) vs Agents-as-Tools (centralized)
  04-guardrails-sessions-tracing-mcp.ipynb  # InputGuardrail, OutputGuardrail, SQLiteSession, tracing, MCP servers
  05-capstone-customer-service.ipynb     # Full multi-agent customer service system

demos/customer-service/      # Chainlit demo app
  app.py                     # Entry point — `chainlit run app.py`
  agents_def.py              # 4 agents: Triage, OrderSpecialist, RefundSpecialist, AbuseDetector
  tools.py                   # lookup_order, list_customer_orders, calculate_refund, process_refund
  models.py                  # Pydantic models (AbuseCheck, RefundDecision, OrderStatus, CustomerContext)
  config.py                  # Mock databases + constants

customer-service-agent/chatkit/  # ChatKit (production UI) demo
  backend/                   # FastAPI — `uvicorn backend.main:app --reload --port 8000`
    main.py, server.py, agents.py, store.py
  frontend/                  # React/Vite — `npm run dev` on port 5173
  run.sh                     # One-command launcher for both

assets/
  openai-agents-sdk-docs-llmstxt.txt  # Full SDK docs reference (use this for SDK questions)
  oai-ag-sdk-cheatsheet.pdf           # Quick-reference cheatsheet
  oai-agents-sdk-nuances.pdf          # SDK subtleties & best practices
  resources.md                        # External links and references
  *.png                               # 10 architecture/concept diagrams

presentation/                # Slides (PDF + HTML)
requirements/                # requirements.in (source) → requirements.txt (locked)
scripts/                     # Reserved for standalone scripts (currently empty)
```

## Key SDK Patterns

```python
# Core imports used across notebooks
from agents import Agent, Runner, function_tool
from agents import InputGuardrail, OutputGuardrail, GuardrailFunctionOutput
from agents import RunContextWrapper, InputGuardrailTripwireTriggered
from agents import SQLiteSession                          # Persistent conversation memory
from agents.extensions.models.litellm_model import LitellmModel  # Non-OpenAI providers

# Execution modes
Runner.run_sync(agent, input)          # Synchronous
await Runner.run(agent, input)         # Async
Runner.run_streamed(agent, input)      # Streaming

# MCP integration
from agents.mcp import MCPServerStdio, MCPServerSse, MCPServerStreamableHttp
```

## Multi-Agent Architecture (Demo Apps)

Both demos share the same agent graph:
```
User → TriageAgent → OrderSpecialist (lookup_order, list_customer_orders)
                   → RefundSpecialist (calculate_refund, process_refund)
       AbuseDetector (InputGuardrail on TriageAgent)
```
- Chainlit demo: rapid prototyping UI, SQLite sessions, streaming
- ChatKit demo: production React frontend, FastAPI backend, OpenAI ChatKit protocol

## Development Notes

- No test suite — all code runs in notebooks or demo apps
- Follow `NN-description.ipynb` naming for new notebooks
- SDK docs available locally: `assets/openai-agents-sdk-docs-llmstxt.txt`
- Demo apps generate SQLite DBs at runtime (gitignored)
- `openai-agents[viz]` installed for agent graph visualization (graphviz)
- `openai-agents[voice]` installed for voice/audio capabilities

## Course Improvement Checklist

When improving this course, consider:
- Are notebook explanations clear for the progression level?
- Do code cells have markdown context before them explaining the "why"?
- Are SDK patterns consistent across notebooks (same model, same import style)?
- Does the capstone (05) actually exercise patterns from all prior notebooks?
- Are the demo apps up to date with the SDK version used in notebooks?
- Do assets/diagrams match current notebook content?
