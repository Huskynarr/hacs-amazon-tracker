"""Constants for the Amazon Package Tracker integration."""
from datetime import timedelta

DOMAIN = "amazon_tracker"
DEFAULT_SCAN_INTERVAL = timedelta(minutes=30)

# IMAP Configuration
CONF_IMAP_SERVER = "imap_server"
CONF_IMAP_PORT = "imap_port"
CONF_IMAP_EMAIL = "imap_email"
CONF_IMAP_PASSWORD = "imap_password"
CONF_IMAP_SSL = "imap_ssl"
CONF_IMAP_FOLDER = "imap_folder"

# Amazon Configuration
CONF_AMAZON_DOMAINS = "amazon_domains"
CONF_TRACKING_DURATION = "tracking_duration"
CONF_SHOW_DELIVERED = "show_delivered"
CONF_DELIVERED_DURATION = "delivered_duration"

# Defaults
DEFAULT_IMAP_PORT = 993
DEFAULT_IMAP_SSL = True
DEFAULT_IMAP_FOLDER = "INBOX"
DEFAULT_TRACKING_DURATION = 14  # days
DEFAULT_SHOW_DELIVERED = True
DEFAULT_DELIVERED_DURATION = 3  # days

# Amazon Domains with email senders
AMAZON_DOMAINS = {
    "amazon.com": {
        "name": "Amazon.com (United States)",
        "sender": "order-update@amazon.com",
        "language": "en",
    },
    "amazon.de": {
        "name": "Amazon.de (Germany)",
        "sender": "order-update@amazon.de",
        "language": "de",
    },
    "amazon.fr": {
        "name": "Amazon.fr (France)",
        "sender": "order-update@amazon.fr",
        "language": "fr",
    },
    "amazon.co.uk": {
        "name": "Amazon.co.uk (United Kingdom)",
        "sender": "order-update@amazon.co.uk",
        "language": "en",
    },
    "amazon.ie": {
        "name": "Amazon.ie (Ireland)",
        "sender": "order-update@amazon.ie",
        "language": "en",
    },
    "amazon.es": {
        "name": "Amazon.es (Spain)",
        "sender": "order-update@amazon.es",
        "language": "es",
    },
    "amazon.it": {
        "name": "Amazon.it (Italy)",
        "sender": "order-update@amazon.it",
        "language": "it",
    },
}

DEFAULT_DOMAIN = "amazon.de"

# Email Subject Patterns for status detection (multilingual)
EMAIL_SUBJECTS = {
    "shipped": [
        r"[Vv]ersandt",  # German
        r"[Ss]hipped",  # English
        r"[Ee]xpédié",  # French
        r"[Ee]nviado",  # Spanish
    ],
    "out_for_delivery": [
        r"[Zz]ustellung heute",  # German
        r"[Oo]ut for [Dd]elivery",  # English
        r"[Ll]ivraison aujourd'hui",  # French
        r"[Ee]n reparto",  # Spanish
    ],
    "delivered": [
        r"[Zz]ugestellt",  # German
        r"[Gg]eliefert",  # German alt
        r"[Dd]elivered",  # English
        r"[Ll]ivré",  # French
        r"[Ee]ntregado",  # Spanish
    ],
    "ordered": [
        r"[Bb]estätigung",  # German
        r"[Bb]estellung",  # German
        r"[Cc]onfirmation",  # English/French
        r"[Oo]rder",  # English
        r"[Cc]onfirmación",  # Spanish
    ],
}

# Status priority (higher index = more progress, never go backwards)
STATUS_PRIORITY = {
    "ordered": 0,
    "shipped": 1,
    "out_for_delivery": 2,
    "delivered": 3,
}

# Carrier-specific tracking number patterns
TRACKING_PATTERNS = {
    "DHL": [
        r"\b(\d{12,14})\b",  # Standard DHL
        r"\b(JJD\d{18})\b",  # DHL Paket
        r"\b(\d{20})\b",  # DHL long format
    ],
    "DPD": [
        r"\b(\d{14})\b",  # DPD standard
        r"\b(0\d{13})\b",  # DPD alt
    ],
    "Hermes": [
        r"\b(\d{16})\b",  # Hermes standard
    ],
    "UPS": [
        r"\b(1Z[A-Z0-9]{16})\b",  # UPS
    ],
    "GLS": [
        r"\b(\d{11,12})\b",  # GLS
    ],
    "FedEx": [
        r"\b(\d{12,15})\b",  # FedEx
    ],
    "Amazon Logistics": [
        r"\b(TB[A-Z0-9]{10,12})\b",  # Amazon Logistics
    ],
    "Deutsche Post": [
        r"\b(R[A-Z]{1}\d{9}DE)\b",  # Deutsche Post Einschreiben
    ],
}

# Carrier detection patterns in email body
CARRIER_PATTERNS = {
    "de": [
        (r"(?:mit|durch|per)\s+(DHL|DPD|Hermes|UPS|GLS|FedEx|Deutsche Post|Amazon Logistics)", None),
        (r"(DHL|DPD|Hermes|UPS|GLS|FedEx|Deutsche Post|Amazon Logistics)\s+Trackingnummer", None),
    ],
    "en": [
        (r"(?:with|by|via)\s+(DHL|DPD|Hermes|UPS|GLS|FedEx|Amazon Logistics|Royal Mail|USPS)", None),
        (r"(DHL|DPD|Hermes|UPS|GLS|FedEx|Amazon Logistics|Royal Mail|USPS)\s+[Tt]racking", None),
    ],
    "fr": [
        (r"(?:avec|par|via)\s+(DHL|DPD|Hermes|UPS|GLS|FedEx|Amazon Logistics|Colissimo|Chronopost)", None),
        (r"(DHL|DPD|Hermes|UPS|GLS|FedEx|Amazon Logistics|Colissimo|Chronopost)\s+[Nn]uméro", None),
    ],
    "es": [
        (r"(?:con|por|via)\s+(DHL|DPD|Hermes|UPS|GLS|FedEx|Amazon Logistics|Correos|SEUR)", None),
        (r"(DHL|DPD|Hermes|UPS|GLS|FedEx|Amazon Logistics|Correos|SEUR)\s+[Ss]eguimiento", None),
    ],
}

# Storage
STORAGE_KEY = f"{DOMAIN}_packages"
STORAGE_VERSION = 1

# Attributes
ATTR_TRACKING_NUMBER = "tracking_number"
ATTR_CARRIER = "carrier"
ATTR_ESTIMATED_DELIVERY = "estimated_delivery"
ATTR_ORDER_DATE = "order_date"
ATTR_ORDER_NUMBER = "order_number"
ATTR_PRODUCT_NAME = "product_name"
ATTR_STATUS = "status"
ATTR_LAST_UPDATED = "last_updated"

# Status values (lowercase)
STATUS_ORDERED = "ordered"
STATUS_SHIPPED = "shipped"
STATUS_OUT_FOR_DELIVERY = "out_for_delivery"
STATUS_DELIVERED = "delivered"

# Order number pattern
ORDER_NUMBER_PATTERN = r"\d{3}-\d{7}-\d{7}"
