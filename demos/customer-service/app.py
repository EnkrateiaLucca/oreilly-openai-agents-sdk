# /// script
# requires-python = ">=3.11"
# dependencies = ["openai-agents", "chainlit", "pydantic", "python-dotenv"]
# ///
"""
Chainlit chat UI for the multi-agent customer service system.

Run with:
    chainlit run app.py --port 8080
"""

import uuid

import chainlit as cl
from dotenv import load_dotenv
from openai.types.responses import ResponseTextDeltaEvent

from agents import InputGuardrailTripwireTriggered, Runner, SQLiteSession
from agents_def import triage_agent  # renamed import to avoid clash with `agents` package
from config import SESSION_DB_PATH, get_customer_context

load_dotenv()


@cl.on_chat_start
async def on_chat_start():
    """Initialize the customer session (default: Alice, a premium customer)."""
    ctx = get_customer_context("CUST-123")
    session_id = f"alice-{uuid.uuid4().hex[:8]}"
    session = SQLiteSession(session_id=session_id, db_path=SESSION_DB_PATH)

    cl.user_session.set("customer_context", ctx)
    cl.user_session.set("session", session)

    await cl.Message(
        content=(
            f"Welcome, **{ctx.customer_name}**! "
            "I'm your customer service assistant.\n\n"
            "You can ask me about your orders, request refunds, or get help "
            "with anything else. How can I help you today?"
        )
    ).send()


@cl.on_message
async def on_message(message: cl.Message):
    """Stream the agent response, visualizing tool calls and guardrail blocks."""
    ctx = cl.user_session.get("customer_context")
    session = cl.user_session.get("session")

    try:
        result = Runner.run_streamed(
            triage_agent,
            message.content,
            context=ctx,
            session=session,
        )

        tool_steps: dict[str, cl.Step] = {}
        msg: cl.Message | None = None  # lazy — created on first text token

        async def _ensure_msg() -> cl.Message:
            nonlocal msg
            if msg is None:
                msg = cl.Message(content="")
                await msg.send()
            return msg

        async for event in result.stream_events():
            # --- Tool calls and outputs ---
            if event.type == "run_item_stream_event":
                item = event.item

                if item.type == "tool_call_item":
                    raw = item.raw_item
                    name = raw.name if hasattr(raw, "name") else raw.get("name", "tool")
                    call_id = raw.call_id if hasattr(raw, "call_id") else raw.get("call_id")
                    args = raw.arguments if hasattr(raw, "arguments") else raw.get("arguments", "")
                    step = cl.Step(name=name, type="tool")
                    step.input = args
                    await step.send()
                    if call_id:
                        tool_steps[call_id] = step

                elif item.type == "tool_call_output_item":
                    raw = item.raw_item
                    call_id = raw.call_id if hasattr(raw, "call_id") else raw.get("call_id")
                    if call_id and call_id in tool_steps:
                        tool_steps[call_id].output = str(item.output)
                        await tool_steps[call_id].update()

            # --- Token-by-token streaming ---
            elif event.type == "raw_response_event":
                if isinstance(event.data, ResponseTextDeltaEvent):
                    m = await _ensure_msg()
                    await m.stream_token(event.data.delta)

        # Finalize whatever message is still open
        if msg is not None:
            await msg.update()

    except InputGuardrailTripwireTriggered:
        await cl.Message(
            content=(
                "I'm sorry, but I can't process messages that contain abusive or "
                "inappropriate language. Please rephrase your request and I'll be "
                "happy to help."
            )
        ).send()
