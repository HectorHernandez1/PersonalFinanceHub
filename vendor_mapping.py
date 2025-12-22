"""
Vendor to Category Mapping

This module contains a mapping of known vendor names to their spending categories.
This allows for quick categorization without needing to call the OpenAI API.
"""

# Dictionary mapping vendor name patterns to categories
# Keys are lowercase patterns to match against merchant names
# Values must match EXACTLY with category_name in database.sql
VENDOR_CATEGORY_MAP = {
    # Hobby
    "global bike": "Hobby",
    "MBO": "Hobby",
    "rapha": "Hobby",
    "specialized": "Hobby",

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
    "COSTCO WHSE": "Groceries",
    "costco.com": "Groceries",
    "grocery": "Groceries",
    "supermarket": "Groceries",
    "Los Altos Ranch Market": "Groceries",

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
    "VISIBLE 866": "Utilities",
    "CITY OF CHANDLER": "Utilities",
    "COX PHOENIX": "Utilities",

    # Transportation
    "uber": "Transportation",
    "lyft": "Transportation",
    "taxi": "Transportation",
    "airline": "Transportation",
    "hotel": "Transportation",
    "parking": "Transportation",
    "transit": "Transportation",
    "COSTCO GAS": "Transportation",

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
    "spotify": "Subscriptions",
    "YouTubePremium": "Subscriptions",
    "Openai *chatgpt": "Subscriptions",
    "Claude.Ai Subscription": "Subscriptions",
    "netflix": "Subscriptions",
    "hulu": "Subscriptions",
    "disney": "Subscriptions",


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

    merchant_lower = merchant_name.lower()

    # Check for exact matches first
    if merchant_lower in VENDOR_CATEGORY_MAP:
        return VENDOR_CATEGORY_MAP[merchant_lower]

    # Check for partial matches (substring matching)
    for vendor_pattern, category in VENDOR_CATEGORY_MAP.items():
        if vendor_pattern.lower() in merchant_lower:
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
