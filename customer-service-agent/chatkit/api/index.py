"""Vercel serverless entry point — FastAPI app with both ChatKit and simple chat endpoints."""

from __future__ import annotations

import json
import os
import sys
import traceback
from pathlib import Path

# Ensure the chatkit project root is on sys.path so `backend.*` imports resolve.
PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from fastapi import FastAPI, Request  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from fastapi.responses import JSONResponse, StreamingResponse  # noqa: E402

from agents import InputGuardrailTripwireTriggered, Runner  # noqa: E402
from backend.agents import (  # noqa: E402
    CUSTOMERS_DB,
    CustomerContext,
    triage_agent,
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/chat")
async def chat_endpoint(request: Request):
    """Simple streaming chat endpoint — no ChatKit protocol needed."""
    try:
        body = await request.json()
        message = body.get("message", "")
        api_key = body.get("api_key", "")
        history = body.get("history", [])

        if not api_key:
            return JSONResponse({"error": "Missing API key"}, status_code=401)
        if not message:
            return JSONResponse({"error": "Missing message"}, status_code=400)

        os.environ["OPENAI_API_KEY"] = api_key

        # Build input with conversation history
        input_messages = []
        for msg in history:
            input_messages.append(
                {"role": msg["role"], "content": msg["content"]}
            )
        input_messages.append({"role": "user", "content": message})

        customer_id = request.query_params.get("customer", "CUST-123")
        cust = CUSTOMERS_DB.get(customer_id, CUSTOMERS_DB["CUST-123"])
        customer_ctx = CustomerContext(
            customer_id=customer_id,
            customer_name=cust["name"],
            is_premium=cust["is_premium"],
        )

        async def stream():
            try:
                result = Runner.run_streamed(
                    triage_agent,
                    input_messages,
                    context=customer_ctx,
                )
                async for event in result.stream_events():
                    if (
                        event.type == "raw_response_event"
                        and hasattr(event.data, "delta")
                        and event.data.delta
                    ):
                        chunk = json.dumps({"delta": event.data.delta})
                        yield f"data: {chunk}\n\n"

                yield "data: [DONE]\n\n"
            except InputGuardrailTripwireTriggered:
                error_msg = json.dumps(
                    {
                        "delta": "Your message was flagged as inappropriate. "
                        "Please rephrase your request respectfully."
                    }
                )
                yield f"data: {error_msg}\n\n"
                yield "data: [DONE]\n\n"
            except Exception as e:
                error_msg = json.dumps({"error": str(e)})
                yield f"data: {error_msg}\n\n"
                yield "data: [DONE]\n\n"

        return StreamingResponse(stream(), media_type="text/event-stream")

    except Exception as e:
        return JSONResponse(
            {"error": str(e), "traceback": traceback.format_exc()},
            status_code=500,
        )


@app.get("/api/health")
async def health():
    return {"status": "ok"}
