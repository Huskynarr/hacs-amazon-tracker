"""Constants for the Amazon Package Tracker integration."""
from datetime import timedelta

DOMAIN = "amazon_tracker"
DEFAULT_SCAN_INTERVAL = timedelta(minutes=30)

# Configuration
CONF_EMAIL = "email"
CONF_PASSWORD = "password"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_DOMAIN = "amazon_domain"

# Amazon Domains
AMAZON_DOMAINS = {
    "amazon.com": {
        "name": "Amazon.com (United States)",
        "base_url": "https://www.amazon.com",
        "language": "en",
    },
    "amazon.de": {
        "name": "Amazon.de (Germany)",
        "base_url": "https://www.amazon.de",
        "language": "de",
    },
    "amazon.fr": {
        "name": "Amazon.fr (France)",
        "base_url": "https://www.amazon.fr",
        "language": "fr",
    },
    "amazon.co.uk": {
        "name": "Amazon.co.uk (United Kingdom)",
        "base_url": "https://www.amazon.co.uk",
        "language": "en",
    },
    "amazon.ie": {
        "name": "Amazon.ie (Ireland)",
        "base_url": "https://www.amazon.ie",
        "language": "en",
    },
}

DEFAULT_DOMAIN = "amazon.de"

# Attributes
ATTR_TRACKING_NUMBER = "tracking_number"
ATTR_CARRIER = "carrier"
ATTR_ESTIMATED_DELIVERY = "estimated_delivery"
ATTR_ORDER_DATE = "order_date"
ATTR_ORDER_NUMBER = "order_number"
ATTR_PRODUCT_NAME = "product_name"
ATTR_STATUS = "status"

# Status
STATUS_IN_TRANSIT = "In Transit"
STATUS_ORDERED = "Ordered"
STATUS_DELIVERED = "Delivered" 