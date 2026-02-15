"""Email parser for Amazon package notifications."""
from __future__ import annotations

import email
import email.policy
import logging
import re
from datetime import datetime, date
from email.message import EmailMessage
from html.parser import HTMLParser
from typing import Any

from .const import (
    AMAZON_DOMAINS,
    CARRIER_PATTERNS,
    EMAIL_SUBJECTS,
    ORDER_NUMBER_PATTERN,
    STATUS_ORDERED,
    STATUS_PRIORITY,
    TRACKING_PATTERNS,
)

_LOGGER = logging.getLogger(__name__)


class _HTMLTextExtractor(HTMLParser):
    """Extract plain text from HTML."""

    def __init__(self):
        super().__init__()
        self._text_parts: list[str] = []
        self._skip = False

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self._skip = True
        elif tag == "br":
            self._text_parts.append("\n")
        elif tag in ("p", "div", "tr", "li"):
            self._text_parts.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self._skip = False

    def handle_data(self, data):
        if not self._skip:
            self._text_parts.append(data)

    def get_text(self) -> str:
        return "".join(self._text_parts)


def _html_to_text(html: str) -> str:
    """Convert HTML to plain text."""
    extractor = _HTMLTextExtractor()
    extractor.feed(html)
    return extractor.get_text()


def _get_email_body(msg: EmailMessage) -> str:
    """Extract body text from an email message."""
    body = ""

    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain":
                charset = part.get_content_charset() or "utf-8"
                payload = part.get_payload(decode=True)
                if payload:
                    body = payload.decode(charset, errors="replace")
                    break
            elif content_type == "text/html":
                charset = part.get_content_charset() or "utf-8"
                payload = part.get_payload(decode=True)
                if payload:
                    html = payload.decode(charset, errors="replace")
                    body = _html_to_text(html)
    else:
        content_type = msg.get_content_type()
        charset = msg.get_content_charset() or "utf-8"
        payload = msg.get_payload(decode=True)
        if payload:
            text = payload.decode(charset, errors="replace")
            if content_type == "text/html":
                body = _html_to_text(text)
            else:
                body = text

    return body


class AmazonEmailParser:
    """Parse Amazon notification emails into package data."""

    def __init__(self, domains: list[str]) -> None:
        """Initialize with list of Amazon domains to monitor."""
        self._valid_senders: set[str] = set()
        self._domain_languages: dict[str, str] = {}

        for domain_key in domains:
            domain_config = AMAZON_DOMAINS.get(domain_key)
            if domain_config:
                sender = domain_config["sender"]
                self._valid_senders.add(sender.lower())
                self._domain_languages[sender.lower()] = domain_config["language"]

    def _is_valid_sender(self, from_addr: str) -> bool:
        """Check if sender is a known Amazon order-update address."""
        if not from_addr:
            return False
        # Extract email from "Name <email>" format
        match = re.search(r"<([^>]+)>", from_addr)
        addr = match.group(1) if match else from_addr
        return addr.lower().strip() in self._valid_senders

    def _get_language_for_sender(self, from_addr: str) -> str:
        """Get language code for a sender address."""
        match = re.search(r"<([^>]+)>", from_addr)
        addr = match.group(1) if match else from_addr
        return self._domain_languages.get(addr.lower().strip(), "en")

    def _detect_status(self, subject: str) -> str:
        """Detect package status from email subject."""
        for status, patterns in EMAIL_SUBJECTS.items():
            for pattern in patterns:
                if re.search(pattern, subject):
                    return status
        return STATUS_ORDERED

    def _extract_order_number(self, text: str) -> str | None:
        """Extract Amazon order number from text."""
        match = re.search(ORDER_NUMBER_PATTERN, text)
        return match.group(0) if match else None

    def _extract_carrier(self, body: str, language: str) -> str | None:
        """Extract carrier name from email body."""
        patterns = CARRIER_PATTERNS.get(language, CARRIER_PATTERNS.get("en", []))
        for pattern, _ in patterns:
            match = re.search(pattern, body)
            if match:
                return match.group(1)
        return None

    def _extract_tracking_number(self, body: str, carrier: str | None) -> str | None:
        """Extract tracking number from email body."""
        # If carrier is known, use carrier-specific patterns
        if carrier and carrier in TRACKING_PATTERNS:
            for pattern in TRACKING_PATTERNS[carrier]:
                match = re.search(pattern, body)
                if match:
                    return match.group(1)

        # Generic tracking number search near keywords
        tracking_keywords = [
            r"[Tt]racking[- ]?(?:[Nn]ummer|[Nn]umber|ID|[Nn]uméro|[Nn]úmero)",
            r"[Ss]endungsnummer",
            r"[Pp]aketnummer",
        ]
        for keyword in tracking_keywords:
            pattern = keyword + r"[:\s]+([A-Z0-9]{8,30})"
            match = re.search(pattern, body)
            if match:
                return match.group(1)

        return None

    def _extract_delivery_date(self, body: str) -> str | None:
        """Extract estimated delivery date from email body."""
        # German date patterns
        date_patterns = [
            # "Zustellung am Montag, 15. Januar"
            r"[Zz]ustellung (?:am|bis)?\s*\w+,?\s*(\d{1,2})\.\s*(\w+)",
            # "Lieferung am 15.01.2024" or "15.01.2024"
            r"[Ll]ieferung\s+(?:am\s+)?(\d{1,2})\.(\d{1,2})\.(\d{4})",
            # "delivery by Monday, January 15"
            r"[Dd]elivery\s+(?:by|on)\s+\w+,?\s+(\w+)\s+(\d{1,2})",
            # "arriving Monday, January 15"
            r"[Aa]rriving\s+\w+,?\s+(\w+)\s+(\d{1,2})",
            # "livraison le lundi 15 janvier"
            r"[Ll]ivraison\s+(?:le\s+)?\w+\s+(\d{1,2})\s+(\w+)",
            # Generic date: dd.mm.yyyy
            r"(\d{1,2})\.(\d{1,2})\.(\d{4})",
        ]

        german_months = {
            "januar": 1, "februar": 2, "märz": 3, "april": 4,
            "mai": 5, "juni": 6, "juli": 7, "august": 8,
            "september": 9, "oktober": 10, "november": 11, "dezember": 12,
        }
        english_months = {
            "january": 1, "february": 2, "march": 3, "april": 4,
            "may": 5, "june": 6, "july": 7, "august": 8,
            "september": 9, "october": 10, "november": 11, "december": 12,
        }
        french_months = {
            "janvier": 1, "février": 2, "mars": 3, "avril": 4,
            "mai": 5, "juin": 6, "juillet": 7, "août": 8,
            "septembre": 9, "octobre": 10, "novembre": 11, "décembre": 12,
        }
        all_months = {**german_months, **english_months, **french_months}

        for pattern in date_patterns:
            match = re.search(pattern, body)
            if not match:
                continue

            groups = match.groups()
            try:
                if len(groups) == 3 and groups[2].isdigit() and len(groups[2]) == 4:
                    # dd.mm.yyyy format
                    d = int(groups[0])
                    m = int(groups[1])
                    y = int(groups[2])
                    return date(y, m, d).isoformat()
                elif len(groups) == 2:
                    # Day + month name or month name + day
                    g0, g1 = groups
                    if g0.isdigit():
                        day = int(g0)
                        month_name = g1.lower()
                    elif g1.isdigit():
                        day = int(g1)
                        month_name = g0.lower()
                    else:
                        continue

                    month_num = all_months.get(month_name)
                    if month_num:
                        year = datetime.now().year
                        delivery = date(year, month_num, day)
                        # If date is in the past, assume next year
                        if delivery < date.today():
                            delivery = date(year + 1, month_num, day)
                        return delivery.isoformat()
            except (ValueError, KeyError):
                continue

        return None

    def _extract_product_name(self, body: str) -> str | None:
        """Extract product name from email body."""
        # Look for product name patterns
        patterns = [
            # Common Amazon email format
            r"(?:Artikel|Item|Article|Producto):\s*(.+?)(?:\n|$)",
            r"(?:Produktname|Product name|Nom du produit):\s*(.+?)(?:\n|$)",
            # Quoted product names
            r'"([^"]{5,100})"',
        ]
        for pattern in patterns:
            match = re.search(pattern, body)
            if match:
                name = match.group(1).strip()
                if len(name) > 5:
                    return name[:100]
        return None

    def parse_email(self, raw_bytes: bytes) -> dict[str, Any] | None:
        """Parse a raw email into package data.

        Returns None if the email is not from a valid Amazon sender
        or does not contain package information.
        """
        try:
            msg = email.message_from_bytes(raw_bytes, policy=email.policy.default)
        except Exception:
            _LOGGER.debug("Failed to parse email bytes")
            return None

        from_addr = msg.get("From", "")
        if not self._is_valid_sender(from_addr):
            return None

        subject = msg.get("Subject", "")
        language = self._get_language_for_sender(from_addr)
        body = _get_email_body(msg)

        # Extract order number from subject or body
        order_number = self._extract_order_number(subject)
        if not order_number:
            order_number = self._extract_order_number(body)

        if not order_number:
            _LOGGER.debug("No order number found in email: %s", subject)
            return None

        status = self._detect_status(subject)
        carrier = self._extract_carrier(body, language)
        tracking_number = self._extract_tracking_number(body, carrier)
        delivery_date = self._extract_delivery_date(body)
        product_name = self._extract_product_name(body)

        # Get email date
        email_date = msg.get("Date", "")
        try:
            parsed_date = email.utils.parsedate_to_datetime(email_date)
            email_date_str = parsed_date.isoformat()
        except Exception:
            email_date_str = datetime.now().isoformat()

        return {
            "order_number": order_number,
            "status": status,
            "carrier": carrier,
            "tracking_number": tracking_number,
            "estimated_delivery": delivery_date,
            "product_name": product_name,
            "last_updated": email_date_str,
            "order_date": email_date_str,
        }


def build_imap_search_query(domains: list[str], since_date: date) -> str:
    """Build an IMAP SEARCH query for Amazon notification emails."""
    senders = []
    for domain_key in domains:
        domain_config = AMAZON_DOMAINS.get(domain_key)
        if domain_config:
            senders.append(domain_config["sender"])

    since_str = since_date.strftime("%d-%b-%Y")

    if not senders:
        return f"(SINCE {since_str})"

    if len(senders) == 1:
        return f'(FROM "{senders[0]}" SINCE {since_str})'

    # Multiple senders: OR query
    # IMAP OR takes exactly 2 arguments, so we need to nest them
    parts = [f'FROM "{s}"' for s in senders]
    query = parts[0]
    for part in parts[1:]:
        query = f"OR {query} {part}"

    return f"({query} SINCE {since_str})"
