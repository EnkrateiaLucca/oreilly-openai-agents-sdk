# Customer Service Agent — ChatKit Demo

Production-style customer service chat agent built with **OpenAI Agents SDK** + **ChatKit**.

## Architecture

```
React Frontend (ChatKit)  →  POST /chatkit  →  FastAPI Backend
                                                    │
                                              ChatKitServer
                                                    │
                                              TriageAgent
                                              ├── OrderSpecialist
                                              └── RefundSpecialist
```

- **Frontend**: `@openai/chatkit-react` — OpenAI's production chat UI component
- **Backend**: `openai-chatkit` (`ChatKitServer`) bridging to `openai-agents` SDK
- **Agents**: Triage agent with specialist sub-agents as tools, abuse guardrail

## Quick Start

```bash
# Requires: conda env 'openai-agents-sdk', Node.js, OPENAI_API_KEY set
./run.sh
# Open http://localhost:5173
```

### Manual Start

```bash
# Terminal 1 — Backend
conda activate openai-agents-sdk
cd chatkit
uvicorn backend.main:app --reload --port 8000

# Terminal 2 — Frontend
cd chatkit/frontend
npm install
npx vite --port 5173
```

## Files

| File | Purpose |
|------|---------|
| `backend/main.py` | FastAPI app with `/chatkit` endpoint |
| `backend/server.py` | `ChatKitServer` subclass — bridges ChatKit to Agents SDK |
| `backend/agents.py` | Agent definitions, tools, guardrails, mock databases |
| `backend/store.py` | In-memory thread/item store |
| `frontend/src/App.tsx` | React app with ChatKit component |
| `demo-prompts.md` | Ready-to-use test prompts for the demo |
| `run.sh` | One-command launcher for both servers |

## Default Customer

The demo defaults to **Alice Johnson (CUST-123)**, a premium customer.
To switch to Bob, append `?customer=CUST-456` to the backend URL.
