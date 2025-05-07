"""Constants for the Amazon Package Tracker integration."""
from datetime import timedelta

DOMAIN = "amazon_tracker"
DEFAULT_SCAN_INTERVAL = timedelta(minutes=30)

# Configuration
CONF_EMAIL = "email"
CONF_PASSWORD = "password"
CONF_SCAN_INTERVAL = "scan_interval"

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