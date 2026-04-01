"""Customer service agents and tools — powered by OpenAI Agents SDK.

This module contains the same multi-agent architecture as the Streamlit demo
but adapted for ChatKit's AgentContext.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from pydantic import BaseModel

from agents import (
    Agent,
    GuardrailFunctionOutput,
    InputGuardrail,
    RunContextWrapper,
    Runner,
    function_tool,
)
from chatkit.agents import AgentContext

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
# Customer context (embedded inside AgentContext.request_context)
# ---------------------------------------------------------------------------


@dataclass
class CustomerContext:
    customer_id: str
    customer_name: str
    is_premium: bool


# Type alias: the full context that tools receive
FullContext = AgentContext[dict[str, Any]]


def get_customer_context(context: dict[str, Any]) -> CustomerContext:
    """Extract CustomerContext from the request_context dict."""
    return context.get("customer", CustomerContext("CUST-123", "Alice Johnson", True))


# ---------------------------------------------------------------------------
# Guardrail model
# ---------------------------------------------------------------------------


class AbuseCheck(BaseModel):
    is_abusive: bool
    reason: str


# ---------------------------------------------------------------------------
# Tools — access customer data via agent_context.request_context
# ---------------------------------------------------------------------------


@function_tool
async def lookup_order(
    wrapper: RunContextWrapper[FullContext], order_id: str
) -> str:
    """Look up order details by order ID."""
    customer = get_customer_context(wrapper.context.request_context)

    if order_id not in ORDERS_DB:
        return f"Order {order_id} not found."

    order = ORDERS_DB[order_id]
    if order["customer_id"] != customer.customer_id:
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
async def list_customer_orders(wrapper: RunContextWrapper[FullContext]) -> str:
    """List all orders for the current customer."""
    customer = get_customer_context(wrapper.context.request_context)

    customer_orders = [
        f"- {oid}: {o['item']} (${o['price']:.2f}) - {o['status']}"
        for oid, o in ORDERS_DB.items()
        if o["customer_id"] == customer.customer_id
    ]
    if not customer_orders:
        return "No orders found for your account."
    return "Your orders:\n" + "\n".join(customer_orders)


@function_tool
async def calculate_refund(
    wrapper: RunContextWrapper[FullContext], order_id: str, reason: str
) -> str:
    """Calculate refund eligibility and amount for an order."""
    customer = get_customer_context(wrapper.context.request_context)

    if order_id not in ORDERS_DB:
        return f"Order {order_id} not found."

    order = ORDERS_DB[order_id]
    if order["customer_id"] != customer.customer_id:
        return "This order does not belong to your account."

    price = order["price"]
    status = order["status"]

    if status == "processing":
        return f"Order {order_id} can be cancelled for a full refund of ${price:.2f}. Reason: {reason}"
    if status == "shipped":
        if customer.is_premium:
            return f"Premium customer: Eligible for full refund of ${price:.2f} upon return. Reason: {reason}"
        return f"Order in transit. Please wait for delivery to request refund. Reason: {reason}"
    if status == "delivered":
        requires_approval = price > 50
        note = " (Requires manager approval)" if requires_approval else ""
        return f"Refund eligible: ${price:.2f}{note}. Reason: {reason}"
    return f"Unable to process refund for order {order_id}"


@function_tool
async def process_refund(
    wrapper: RunContextWrapper[FullContext], order_id: str
) -> str:
    """Process an approved refund for an order."""
    customer = get_customer_context(wrapper.context.request_context)

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
        f"Thank you for your patience, {customer.customer_name}!"
    )


# ---------------------------------------------------------------------------
# Specialist sub-agents (called as tools by the triage agent)
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
# Wrapper tools: triage calls these to consult specialists
# ---------------------------------------------------------------------------


@function_tool
async def consult_order_specialist(
    wrapper: RunContextWrapper[FullContext], customer_message: str
) -> str:
    """Consult the order specialist for order status, tracking, shipping,
    or listing orders. Pass the customer's message as-is."""
    result = await Runner.run(
        _order_agent, customer_message, context=wrapper.context
    )
    return str(result.final_output)


@function_tool
async def consult_refund_specialist(
    wrapper: RunContextWrapper[FullContext], customer_message: str
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
# Triage agent — the single entry point
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
