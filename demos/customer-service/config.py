"""Mock databases and configuration constants."""

from datetime import datetime, timedelta

DEFAULT_MODEL = "gpt-4.1"
SESSION_DB_PATH = "customer_service.db"
TRIAGE_MODEL = "gpt-4.1"

# Mock order database
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

# Mock customer database
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


def get_customer_context(customer_id: str):
    """Build a CustomerContext from the mock database."""
    from models import CustomerContext

    customer = CUSTOMERS_DB[customer_id]
    return CustomerContext(
        customer_id=customer_id,
        customer_name=customer["name"],
        is_premium=customer["is_premium"],
    )
