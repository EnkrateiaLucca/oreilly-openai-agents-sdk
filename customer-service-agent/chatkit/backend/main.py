"""FastAPI application — serves the /chatkit endpoint and static frontend."""

from __future__ import annotations

from pathlib import Path

from chatkit.server import StreamingResult
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, Response, StreamingResponse
from fastapi.staticfiles import StaticFiles

from .agents import CUSTOMERS_DB, CustomerContext
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


# Serve the built React frontend in production
if FRONTEND_DIR.is_dir():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIR / "assets"), name="assets")

    @app.get("/{path:path}")
    async def serve_frontend(path: str):
        file = FRONTEND_DIR / path
        if file.is_file():
            return FileResponse(file)
        return FileResponse(FRONTEND_DIR / "index.html")
