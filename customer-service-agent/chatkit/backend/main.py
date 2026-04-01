"""FastAPI application — serves the /chatkit endpoint and static frontend."""

from __future__ import annotations

import json
import os
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from agents import InputGuardrailTripwireTriggered, Runner
from chatkit.server import StreamingResult
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, Response, StreamingResponse
from fastapi.staticfiles import StaticFiles
from openai.types.responses import ResponseTextDeltaEvent
from pydantic import BaseModel

from .agents import CUSTOMERS_DB, CustomerContext, triage_agent
from .server import CustomerServiceServer

app = FastAPI(title="Customer Service ChatKit API")

# CORS — allow the Vite dev server and any localhost origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

chatkit_server = CustomerServiceServer()

# Resolve frontend build directory (if it exists)
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend" / "dist"


@app.post("/chatkit")
async def chatkit_endpoint(request: Request) -> Response:
    """Single endpoint that handles ALL ChatKit operations (read + stream)."""

    # BYOK: read the user-supplied API key from the request header.
    # Falls back to the server's env var if no header is sent (local dev).
    api_key = request.headers.get("x-openai-api-key") or os.environ.get(
        "OPENAI_API_KEY"
    )
    if not api_key:
        return JSONResponse(
            {"error": "Missing OpenAI API key. Please enter your key in the app."},
            status_code=401,
        )
    os.environ["OPENAI_API_KEY"] = api_key

    # Build request context with customer info.
    # For the demo we default to Alice; pass ?customer=CUST-456 for Bob.
    customer_id = request.query_params.get("customer", "CUST-123")
    cust = CUSTOMERS_DB.get(customer_id, CUSTOMERS_DB["CUST-123"])
    customer = CustomerContext(
        customer_id=customer_id,
        customer_name=cust["name"],
        is_premium=cust["is_premium"],
    )

    context = {"customer": customer, "request": request}

    payload = await request.body()
    result = await chatkit_server.process(payload, context)

    if isinstance(result, StreamingResult):
        return StreamingResponse(result, media_type="text/event-stream")
    if hasattr(result, "json"):
        return Response(content=result.json, media_type="application/json")
    return JSONResponse(result)


class ChatRequest(BaseModel):
    message: str
    api_key: str
    history: list[dict[str, Any]] = []


@app.post("/api/chat")
async def api_chat(body: ChatRequest) -> StreamingResponse:
    """Simple streaming chat endpoint for the React frontend."""
    os.environ["OPENAI_API_KEY"] = body.api_key

    # Default to Alice for the demo
    cust = CUSTOMERS_DB["CUST-123"]
    customer = CustomerContext(
        customer_id="CUST-123",
        customer_name=cust["name"],
        is_premium=cust["is_premium"],
    )

    # Build conversation input: include history + new message
    agent_input = [
        {"role": msg["role"], "content": msg["content"]}
        for msg in body.history
        if msg.get("content")
    ] + [{"role": "user", "content": body.message}]

    # Tools expect wrapper.context.request_context = {"customer": ...}
    agent_context = SimpleNamespace(request_context={"customer": customer})

    async def stream():
        try:
            result = Runner.run_streamed(triage_agent, agent_input, context=agent_context)
            full_text = ""
            async for event in result.stream_events():
                if event.type == "raw_response_event" and isinstance(
                    event.data, ResponseTextDeltaEvent
                ):
                    full_text += event.data.delta
                    yield f"data: {json.dumps({'text': full_text})}\n\n"
        except InputGuardrailTripwireTriggered:
            yield f"data: {json.dumps({'error': 'Message flagged as inappropriate. Please rephrase.'})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")


# Serve the built React frontend in production
if FRONTEND_DIR.is_dir():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIR / "assets"), name="assets")

    @app.get("/{path:path}")
    async def serve_frontend(path: str):
        file = FRONTEND_DIR / path
        if file.is_file():
            return FileResponse(file)
        return FileResponse(FRONTEND_DIR / "index.html")
