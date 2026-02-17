"""Pydantic models and dataclasses for the customer service system."""

from dataclasses import dataclass
from typing import Optional

from pydantic import BaseModel, Field


class OrderStatus(BaseModel):
    """Order status information."""

    order_id: str
    item: str
    status: str
    tracking_number: Optional[str] = None
    eta: Optional[str] = None


class RefundDecision(BaseModel):
    """Refund processing decision."""

    order_id: str
    eligible: bool
    refund_amount: float
    reason: str
    requires_approval: bool = Field(description="True if refund > $50")


class AbuseCheck(BaseModel):
    """Check for abusive content."""

    is_abusive: bool
    reason: str


@dataclass
class CustomerContext:
    """Context about the current customer, injected into every tool call."""

    customer_id: str
    customer_name: str
    is_premium: bool
