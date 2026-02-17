# Customer Service Demo — Multi-Agent Chat UI

A standalone Chainlit app extracted from the capstone notebook (`notebooks/05-capstone-customer-service.ipynb`). It visualizes agent handoffs, tool calls, and guardrail blocks in real-time.

## Architecture

```
Customer Message
       │
       ▼
┌──────────────────┐
│   TriageAgent    │──── [Input Guardrail: Block abuse]
│   (Router)       │
└──────────────────┘
       │ handoff
       ├─────────────────────┐
       ▼                     ▼
┌──────────────────┐  ┌──────────────────┐
│  OrderSpecialist │  │ RefundSpecialist  │
│  - lookup_order  │  │  - calc_refund    │
│  - list_orders   │  │  - process_refund │
└──────────────────┘  └──────────────────┘
       │                     │
       └─────────────────────┘
                 │
                 ▼
        [Session Memory]
```

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set your API key
cp .env.example .env
# Edit .env and add your OpenAI API key

# 3. Run the app
chainlit run app.py
```

The UI opens at http://localhost:8000.

## What the Demo Shows

| Feature | What you'll see in the UI |
|---------|--------------------------|
| **Handoffs** | "Handoff → OrderSpecialist" step appears when triage routes |
| **Tool calls** | Collapsible steps showing tool name, arguments, and output |
| **Streaming** | Tokens appear word-by-word as the agent generates |
| **Guardrails** | Abusive messages get a polite block message |
| **Session memory** | Follow-up questions remember earlier context |

## Sample Messages to Try

1. `Check on order ORD-001` — handoff to OrderSpecialist + lookup_order tool
2. `What are all my orders?` — list_customer_orders tool
3. `I want a refund for ORD-002` — handoff to RefundSpecialist + calculate_refund + process_refund
4. `I'm going to destroy you all!` — guardrail blocks the message
5. `This is really frustrating` — frustrated but NOT blocked (guardrail passes)

## File Structure

| File | Role |
|------|------|
| `app.py` | Chainlit entry point — streaming + UI visualization |
| `agents_def.py` | 4 agents + guardrail function |
| `tools.py` | 4 `@function_tool` implementations |
| `models.py` | Pydantic models + CustomerContext dataclass |
| `config.py` | Mock databases + constants |
