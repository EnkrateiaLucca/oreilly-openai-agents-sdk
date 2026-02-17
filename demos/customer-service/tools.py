"""Business logic tools for the customer service agents."""

from agents import RunContextWrapper, function_tool
from config import ORDERS_DB
from models import CustomerContext


@function_tool
async def lookup_order(wrapper: RunContextWrapper[CustomerContext], order_id: str) -> str:
    """Look up order details by order ID."""
    ctx = wrapper.context

    if order_id not in ORDERS_DB:
        return f"Order {order_id} not found."

    order = ORDERS_DB[order_id]

    if order["customer_id"] != ctx.customer_id:
        return f"Order {order_id} does not belong to your account."

    return f"""
Order {order_id}:
- Item: {order['item']}
- Price: ${order['price']:.2f}
- Status: {order['status'].upper()}
- Tracking: {order.get('tracking', 'Not yet available')}
- ETA: {order.get('eta', order.get('delivered_date', 'N/A'))}
"""


@function_tool
async def list_customer_orders(wrapper: RunContextWrapper[CustomerContext]) -> str:
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
        return f"Order {order_id} can be cancelled for a full refund of ${price:.2f}. Reason: {reason}"

    if status == "shipped":
        if ctx.is_premium:
            return f"Premium customer: Eligible for full refund of ${price:.2f} upon return. Reason: {reason}"
        return f"Order in transit. Please wait for delivery to request refund. Reason: {reason}"

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

    return f"""Refund processed successfully!
- Order: {order_id}
- Amount: ${price:.2f}
- Method: Original payment method
- Timeline: 3-5 business days

Thank you for your patience, {ctx.customer_name}!"""
