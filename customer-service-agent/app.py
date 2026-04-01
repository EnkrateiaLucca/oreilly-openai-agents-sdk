# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "streamlit",
#     "openai-agents>=0.9.1",
#     "pydantic",
# ]
# ///
"""
Customer Service Chat Agent - Streamlit App
Built with OpenAI Agents SDK 0.9.1

Architecture: Single triage agent with specialist sub-agents wrapped as tools.
The triage agent stays in control, calls specialists, and streams the final
response to the user.

Run with: uv run streamlit run app.py
"""

import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

import streamlit as st
from pydantic import BaseModel, Field

from agents import (
    Agent,
    GuardrailFunctionOutput,
    InputGuardrail,
    InputGuardrailTripwireTriggered,
    RunConfig,
    RunContextWrapper,
    Runner,
    SQLiteSession,
    function_tool,
    trace,
)

# ---------------------------------------------------------------------------
# Mock databases
# ---------------------------------------------------------------------------

ORDERS_DB = {
    "ORD-001": {
        "customer_id": "CUST-123",
        "item": "Wireless Headphones",
        "price": 79.99,
        "status": "shipped",
        "tracking": "1Z999AA10123456784",
        "eta": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"),
    },
    "ORD-002": {
        "customer_id": "CUST-123",
        "item": "Phone Case",
        "price": 19.99,
        "status": "delivered",
        "tracking": "1Z999AA10123456785",
        "delivered_date": (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d"),
    },
    "ORD-003": {
        "customer_id": "CUST-456",
        "item": "USB Cable",
        "price": 12.99,
        "status": "processing",
        "tracking": None,
        "eta": "Pending shipment",
    },
}

CUSTOMERS_DB = {
    "CUST-123": {
        "name": "Alice Johnson",
        "is_premium": True,
        "lifetime_value": 1250.00,
    },
    "CUST-456": {
        "name": "Bob Smith",
        "is_premium": False,
        "lifetime_value": 89.99,
    },
}

# ---------------------------------------------------------------------------
# Structured output models
# ---------------------------------------------------------------------------


class AbuseCheck(BaseModel):
    """Check for abusive content."""

    is_abusive: bool
    reason: str


# ---------------------------------------------------------------------------
# Customer context
# ---------------------------------------------------------------------------


@dataclass
class CustomerContext:
    """Context about the current customer."""

    customer_id: str
    customer_name: str
    is_premium: bool


# ---------------------------------------------------------------------------
# Low-level data tools (used by specialist sub-agents)
# ---------------------------------------------------------------------------


@function_tool
async def lookup_order(
    wrapper: RunContextWrapper[CustomerContext], order_id: str
) -> str:
    """Look up order details by order ID."""
    ctx = wrapper.context

    if order_id not in ORDERS_DB:
        return f"Order {order_id} not found."

    order = ORDERS_DB[order_id]

    if order["customer_id"] != ctx.customer_id:
        return f"Order {order_id} does not belong to your account."

    return (
        f"Order {order_id}:\n"
        f"- Item: {order['item']}\n"
        f"- Price: ${order['price']:.2f}\n"
        f"- Status: {order['status'].upper()}\n"
        f"- Tracking: {order.get('tracking', 'Not yet available')}\n"
        f"- ETA: {order.get('eta', order.get('delivered_date', 'N/A'))}"
    )


@function_tool
async def list_customer_orders(
    wrapper: RunContextWrapper[CustomerContext],
) -> str:
    """List all orders for the current customer."""
    ctx = wrapper.context

    customer_orders = [
        f"- {oid}: {o['item']} (${o['price']:.2f}) - {o['status']}"
        for oid, o in ORDERS_DB.items()
        if o["customer_id"] == ctx.customer_id
    ]

    if not customer_orders:
        return "No orders found for your account."

    return "Your orders:\n" + "\n".join(customer_orders)


@function_tool
async def calculate_refund(
    wrapper: RunContextWrapper[CustomerContext],
    order_id: str,
    reason: str,
) -> str:
    """Calculate refund eligibility and amount for an order."""
    ctx = wrapper.context

    if order_id not in ORDERS_DB:
        return f"Order {order_id} not found."

    order = ORDERS_DB[order_id]

    if order["customer_id"] != ctx.customer_id:
        return "This order does not belong to your account."

    price = order["price"]
    status = order["status"]

    if status == "processing":
        return (
            f"Order {order_id} can be cancelled for a full refund "
            f"of ${price:.2f}. Reason: {reason}"
        )

    if status == "shipped":
        if ctx.is_premium:
            return (
                f"Premium customer: Eligible for full refund of "
                f"${price:.2f} upon return. Reason: {reason}"
            )
        return (
            f"Order in transit. Please wait for delivery to request "
            f"refund. Reason: {reason}"
        )

    if status == "delivered":
        requires_approval = price > 50
        approval_note = " (Requires manager approval)" if requires_approval else ""
        return f"Refund eligible: ${price:.2f}{approval_note}. Reason: {reason}"

    return f"Unable to process refund for order {order_id}"


@function_tool
async def process_refund(
    wrapper: RunContextWrapper[CustomerContext],
    order_id: str,
) -> str:
    """Process an approved refund for an order."""
    ctx = wrapper.context

    if order_id not in ORDERS_DB:
        return f"Order {order_id} not found."

    order = ORDERS_DB[order_id]
    price = order["price"]

    return (
        f"Refund processed successfully!\n"
        f"- Order: {order_id}\n"
        f"- Amount: ${price:.2f}\n"
        f"- Method: Original payment method\n"
        f"- Timeline: 3-5 business days\n\n"
        f"Thank you for your patience, {ctx.customer_name}!"
    )


# ---------------------------------------------------------------------------
# Specialist sub-agents (internal, not exposed via handoffs)
# ---------------------------------------------------------------------------

_order_agent = Agent(
    name="OrderSpecialist",
    instructions=(
        "You help customers with order-related inquiries.\n\n"
        "Capabilities:\n"
        "- Look up order status and tracking\n"
        "- List customer's orders\n"
        "- Provide shipping estimates\n\n"
        "Use your tools to gather the data, then return a clear, "
        "complete answer. Do NOT ask follow-up questions."
    ),
    model="gpt-4.1",
    tools=[lookup_order, list_customer_orders],
)

_refund_agent = Agent(
    name="RefundSpecialist",
    instructions=(
        "You help customers with refunds and returns.\n\n"
        "Process:\n"
        "1. First calculate refund eligibility using calculate_refund\n"
        "2. If eligible, use process_refund to complete it\n"
        "3. If requires approval, explain the timeline\n\n"
        "Use your tools to gather data and process the refund, "
        "then return a clear, complete answer."
    ),
    model="gpt-4.1",
    tools=[calculate_refund, process_refund, lookup_order],
)

# ---------------------------------------------------------------------------
# Wrapper tools: run specialist agents and return their output to triage
# ---------------------------------------------------------------------------


@function_tool
async def consult_order_specialist(
    wrapper: RunContextWrapper[CustomerContext],
    customer_message: str,
) -> str:
    """Consult the order specialist for order status, tracking, shipping,
    or listing orders. Pass the customer's message as-is."""
    result = await Runner.run(
        _order_agent, customer_message, context=wrapper.context
    )
    return str(result.final_output)


@function_tool
async def consult_refund_specialist(
    wrapper: RunContextWrapper[CustomerContext],
    customer_message: str,
) -> str:
    """Consult the refund specialist for refunds, returns, or cancellations.
    Pass the customer's message as-is."""
    result = await Runner.run(
        _refund_agent, customer_message, context=wrapper.context
    )
    return str(result.final_output)


# ---------------------------------------------------------------------------
# Guardrail
# ---------------------------------------------------------------------------

_abuse_detector = Agent(
    name="AbuseDetector",
    instructions=(
        "Detect if customer message is abusive or inappropriate:\n"
        "- Threats or violence\n"
        "- Excessive profanity\n"
        "- Personal attacks on staff\n"
        "- Discriminatory language\n\n"
        "NOTE: Frustrated customers expressing disappointment are NOT abusive. "
        "Only flag truly inappropriate content."
    ),
    model="gpt-4.1",
    output_type=AbuseCheck,
)


async def _abuse_guardrail(ctx, agent, input_data):
    result = await Runner.run(_abuse_detector, input_data, context=ctx.context)
    check = result.final_output_as(AbuseCheck)
    return GuardrailFunctionOutput(
        output_info=check,
        tripwire_triggered=check.is_abusive,
    )


# ---------------------------------------------------------------------------
# Triage agent (single entry point — stays in control)
# ---------------------------------------------------------------------------

triage_agent = Agent(
    name="CustomerServiceAgent",
    instructions=(
        "You are a friendly, professional customer service agent.\n\n"
        "You have two specialist tools:\n"
        "- consult_order_specialist: for order status, tracking, shipping, "
        "or listing orders\n"
        "- consult_refund_specialist: for refunds, returns, or cancellations\n\n"
        "Workflow:\n"
        "1. Understand the customer's issue\n"
        "2. Call the appropriate specialist tool with the customer's message\n"
        "3. Use the specialist's response to compose a polished, friendly "
        "reply to the customer\n\n"
        "IMPORTANT:\n"
        "- Always call a specialist tool before answering order/refund questions. "
        "Do NOT guess or make up order data.\n"
        "- If the question doesn't fit either category, help directly.\n"
        "- Be empathetic, concise, and professional."
    ),
    model="gpt-4.1",
    tools=[consult_order_specialist, consult_refund_specialist],
    input_guardrails=[InputGuardrail(guardrail_function=_abuse_guardrail)],
)

# ---------------------------------------------------------------------------
# Streamlit UI
# ---------------------------------------------------------------------------

st.set_page_config(page_title="Customer Service Agent", page_icon="🎧", layout="wide")
st.title("Customer Service Agent")

# Sidebar – customer selector & info
with st.sidebar:
    st.header("Customer Profile")
    customer_id = st.selectbox(
        "Select customer",
        options=list(CUSTOMERS_DB.keys()),
        format_func=lambda cid: f"{CUSTOMERS_DB[cid]['name']} ({cid})",
    )
    cust = CUSTOMERS_DB[customer_id]
    st.markdown(f"**Name:** {cust['name']}")
    st.markdown(f"**Premium:** {'Yes' if cust['is_premium'] else 'No'}")
    st.markdown(f"**Lifetime value:** ${cust['lifetime_value']:.2f}")

    st.divider()
    st.subheader("Orders")
    for oid, order in ORDERS_DB.items():
        if order["customer_id"] == customer_id:
            st.markdown(
                f"**{oid}** – {order['item']}  \n"
                f"${order['price']:.2f} · {order['status'].upper()}"
            )

    st.divider()
    if st.button("Clear conversation"):
        st.session_state.pop("messages", None)
        st.session_state.pop("session_key", None)
        st.rerun()

# Build context for selected customer
customer_context = CustomerContext(
    customer_id=customer_id,
    customer_name=cust["name"],
    is_premium=cust["is_premium"],
)

# Initialise chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Ensure we reset when switching customers
session_key = f"session_{customer_id}"
if st.session_state.get("session_key") != session_key:
    st.session_state.session_key = session_key
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("How can we help you today?"):
    # Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Run the agent with streaming
    with st.chat_message("assistant"):
        try:
            session = SQLiteSession(
                session_id=session_key,
                db_path="customer_service.db",
            )
            run_config = RunConfig(
                workflow_name="Customer Service",
                trace_include_sensitive_data=True,
            )

            async def _run_streamed():
                with trace("Customer Service Interaction"):
                    result = Runner.run_streamed(
                        triage_agent,
                        prompt,
                        context=customer_context,
                        session=session,
                        run_config=run_config,
                    )
                    # Collect streamed text events
                    full_text = ""
                    async for event in result.stream_events():
                        if event.type == "raw_response_event":
                            from openai.types.responses import (
                                ResponseTextDeltaEvent,
                            )

                            if isinstance(event.data, ResponseTextDeltaEvent):
                                full_text += event.data.delta
                                yield event.data.delta

            # Bridge async generator into a sync generator for st.write_stream
            loop = asyncio.new_event_loop()
            agen = _run_streamed()

            def sync_stream():
                try:
                    while True:
                        chunk = loop.run_until_complete(agen.__anext__())
                        yield chunk
                except StopAsyncIteration:
                    pass
                finally:
                    loop.close()

            reply = st.write_stream(sync_stream())
            st.session_state.messages.append(
                {"role": "assistant", "content": reply}
            )

        except InputGuardrailTripwireTriggered:
            blocked_msg = (
                "Your message was flagged as inappropriate. "
                "Please rephrase your request respectfully and we'll "
                "be happy to help."
            )
            st.warning(blocked_msg)
            st.session_state.messages.append(
                {"role": "assistant", "content": blocked_msg}
            )
