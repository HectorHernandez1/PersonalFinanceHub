"""
Vendor to Category Mapping

This module contains a mapping of known vendor names to their spending categories.
This allows for quick categorization without needing to call the OpenAI API.
"""

# Dictionary mapping vendor name patterns to categories
# Keys are lowercase patterns to match against merchant names
# Values must match EXACTLY with category_name in database.sql
VENDOR_CATEGORY_MAP = {
    # Payments
    "payment": "Payments",
    "paypal": "Payments",
    "venmo": "Payments",
    "stripe": "Payments",
    "square": "Payments",

    # Groceries
    "whole foods": "Groceries",
    "trader joe": "Groceries",
    "safeway": "Groceries",
    "kroger": "Groceries",
    "sprouts": "Groceries",
    "costco": "Groceries",
    "costco.com": "Groceries",
    "grocery": "Groceries",
    "supermarket": "Groceries",

    # Dining
    "restaurant": "Dining",
    "cafe": "Dining",
    "coffee": "Dining",
    "burger": "Dining",
    "pizza": "Dining",
    "sushi": "Dining",
    "bbq": "Dining",
    "diner": "Dining",
    "bar": "Dining",
    "pub": "Dining",

    # Entertainment
    "netflix": "Entertainment",
    "spotify": "Entertainment",
    "hulu": "Entertainment",
    "disney": "Entertainment",
    "movie": "Entertainment",
    "cinema": "Entertainment",
    "theater": "Entertainment",
    "concert": "Entertainment",
    "game": "Entertainment",

    # Utilities
    "electric": "Utilities",
    "water": "Utilities",
    "gas company": "Utilities",
    "internet": "Utilities",
    "phone": "Utilities",
    "comcast": "Utilities",
    "verizon": "Utilities",
    "at&t": "Utilities",
    "t-mobile": "Utilities",

    # Transportation
    "uber": "Transportation",
    "lyft": "Transportation",
    "taxi": "Transportation",
    "airline": "Transportation",
    "hotel": "Transportation",
    "parking": "Transportation",
    "transit": "Transportation",

    # Shopping
    "amazon": "Shopping",
    "walmart": "Shopping",
    "target": "Shopping",
    "bestbuy": "Shopping",
    "mall": "Shopping",
    "store": "Shopping",

    # Healthcare
    "pharmacy": "Healthcare",
    "doctor": "Healthcare",
    "hospital": "Healthcare",
    "clinic": "Healthcare",
    "cvs": "Healthcare",
    "walgreens": "Healthcare",
    "gym": "Healthcare",

    # Dog Care
    "dog": "Dog Care",
    "vet": "Dog Care",
    "pet": "Dog Care",
    "petco": "Dog Care",
    "petsmart": "Dog Care",

    # Subscriptions
    "subscription": "Subscriptions",
    "subscription service": "Subscriptions",

    # Refunds
    "refund": "Refunds & Returns",
    "return": "Refunds & Returns",
    "credit": "Refunds & Returns",
}


def get_category_from_vendor(merchant_name: str) -> str:
    """
    Get the category for a merchant by matching against known vendors.

    Args:
        merchant_name (str): The name of the merchant

    Returns:
        str: The category name if found, None otherwise
    """
    if not merchant_name:
        return None

    merchant_lower = merchant_name.lower()

    # Check for exact matches first
    if merchant_lower in VENDOR_CATEGORY_MAP:
        return VENDOR_CATEGORY_MAP[merchant_lower]

    # Check for partial matches (substring matching)
    for vendor_pattern, category in VENDOR_CATEGORY_MAP.items():
        if vendor_pattern in merchant_lower:
            return category

    return None


def add_vendor_mapping(vendor_name: str, category: str) -> None:
    """
    Add a new vendor mapping dynamically.

    Args:
        vendor_name (str): The vendor name pattern (will be lowercased)
        category (str): The category to assign to this vendor
    """
    VENDOR_CATEGORY_MAP[vendor_name.lower()] = category
