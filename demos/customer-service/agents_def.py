"""Agent definitions: triage, order specialist, refund specialist, and abuse guardrail."""

from agents import Agent, GuardrailFunctionOutput, InputGuardrail, Runner
from config import DEFAULT_MODEL, TRIAGE_MODEL
from models import AbuseCheck, RefundDecision, OrderStatus
from tools import calculate_refund, list_customer_orders, lookup_order, process_refund

# --- Abuse detection guardrail ---

abuse_detector = Agent(
    name="AbuseDetector",
    instructions="""Detect if customer message is abusive or inappropriate:
    - Threats or violence
    - Excessive profanity
    - Personal attacks on staff
    - Discriminatory language

    NOTE: Frustrated customers expressing disappointment are NOT abusive.
    Only flag truly inappropriate content.""",
    model=DEFAULT_MODEL,
    output_type=AbuseCheck,
)


async def abuse_guardrail(ctx, agent, input_data):
    result = await Runner.run(abuse_detector, input_data, context=ctx.context)
    check = result.final_output_as(AbuseCheck)
    return GuardrailFunctionOutput(
        output_info=check,
        tripwire_triggered=check.is_abusive,
    )


# --- Specialist agents (used as tools, not handoffs) ---

order_agent = Agent(
    name="OrderSpecialist",
    instructions="""You help customers with order-related inquiries.

    Capabilities:
    - Look up order status and tracking
    - List customer's orders
    - Provide shipping estimates

    IMPORTANT: Always use your tools (lookup_order, list_customer_orders) to retrieve
    real data BEFORE responding. Never reply with placeholder text like "let me check"
    without actually calling a tool first.

    Be helpful and provide clear, concise information.""",
    model=DEFAULT_MODEL,
    tools=[lookup_order, list_customer_orders],
    output_type=OrderStatus,
)

refund_agent = Agent(
    name="RefundSpecialist",
    instructions="""You help customers with refunds and returns.

    Process:
    1. First calculate refund eligibility using calculate_refund
    2. If eligible, use process_refund to complete it
    3. If requires approval, explain the timeline

    IMPORTANT: Always use your tools (calculate_refund, process_refund, lookup_order)
    to retrieve real data BEFORE responding. Never reply without calling a tool first.

    Be empathetic - customers requesting refunds may be frustrated.
    Always explain the refund policy clearly.""",
    model=DEFAULT_MODEL,
    tools=[calculate_refund, process_refund, lookup_order],
    output_type=RefundDecision,
)

# --- Triage agent (entry point) ---
# Uses specialists as tools so their structured output flows back here,
# and this agent formats a natural-language response for the user.

triage_agent = Agent(
    name="CustomerServiceTriage",
    instructions="""You are the front desk of customer service.

    Your job:
    1. Understand the customer's issue
    2. Call the appropriate specialist tool:
       - If they ask about orders, tracking, or shipping → use the OrderSpecialist tool
       - If they ask about refunds, returns, or cancellations → use the RefundSpecialist tool
    3. Use the structured data returned by the specialist to craft a friendly,
       helpful response to the customer.

    IMPORTANT: Always call a specialist tool for order or refund questions.
    Do NOT answer order or refund questions without calling a tool first.

    If the question doesn't fit either category, help them directly.
    Be professional and empathetic.""",
    model=TRIAGE_MODEL,
    tools=[
        order_agent.as_tool(
            tool_name="order_specialist",
            tool_description="Handle order status, tracking, and shipping inquiries",
        ),
        refund_agent.as_tool(
            tool_name="refund_specialist",
            tool_description="Handle refunds, returns, and cancellations",
        ),
    ],
    input_guardrails=[InputGuardrail(guardrail_function=abuse_guardrail)],
)
