"""Tests for Amazon email parser."""
import email
import email.mime.text
import email.mime.multipart
from datetime import date

import pytest

from custom_components.amazon_tracker.email_parser import (
    AmazonEmailParser,
    build_imap_search_query,
)


def _make_email(
    from_addr: str,
    subject: str,
    body: str,
    content_type: str = "text/plain",
    date_str: str = "Mon, 10 Feb 2025 14:30:00 +0100",
) -> bytes:
    """Create a raw email bytes object for testing."""
    if content_type == "text/html":
        msg = email.mime.multipart.MIMEMultipart("alternative")
        html_part = email.mime.text.MIMEText(body, "html", "utf-8")
        msg.attach(html_part)
    else:
        msg = email.mime.text.MIMEText(body, "plain", "utf-8")

    msg["From"] = from_addr
    msg["Subject"] = subject
    msg["Date"] = date_str
    msg["To"] = "user@example.com"

    return msg.as_bytes()


class TestAmazonEmailParser:
    """Test AmazonEmailParser class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = AmazonEmailParser(["amazon.de", "amazon.com", "amazon.fr"])

    def test_valid_sender_accepted(self):
        """Test that valid Amazon senders are accepted."""
        raw = _make_email(
            from_addr="order-update@amazon.de",
            subject="Versandt: Bestellung 123-4567890-1234567",
            body="Ihr Paket wurde mit DHL Trackingnummer 123456789012 versandt.",
        )
        result = self.parser.parse_email(raw)
        assert result is not None
        assert result["order_number"] == "123-4567890-1234567"

    def test_invalid_sender_rejected(self):
        """Test that non-Amazon senders are rejected."""
        raw = _make_email(
            from_addr="spam@evil.com",
            subject="Versandt: Bestellung 123-4567890-1234567",
            body="Fake package notification.",
        )
        result = self.parser.parse_email(raw)
        assert result is None

    def test_sender_with_display_name(self):
        """Test sender with display name format."""
        raw = _make_email(
            from_addr="Amazon.de <order-update@amazon.de>",
            subject="Versandt: Bestellung 123-4567890-1234567",
            body="Paket mit DHL versandt.",
        )
        result = self.parser.parse_email(raw)
        assert result is not None

    def test_no_order_number_returns_none(self):
        """Test that email without order number is ignored."""
        raw = _make_email(
            from_addr="order-update@amazon.de",
            subject="Amazon Newsletter",
            body="Check out our new deals!",
        )
        result = self.parser.parse_email(raw)
        assert result is None

    # --- German email tests ---

    def test_german_shipped_status(self):
        """Test detection of German shipped status."""
        raw = _make_email(
            from_addr="order-update@amazon.de",
            subject="Versandt: Ihre Bestellung 123-4567890-1234567",
            body="Ihr Paket wurde versandt.",
        )
        result = self.parser.parse_email(raw)
        assert result is not None
        assert result["status"] == "shipped"

    def test_german_delivered_status(self):
        """Test detection of German delivered status."""
        raw = _make_email(
            from_addr="order-update@amazon.de",
            subject="Zugestellt: Bestellung 123-4567890-1234567",
            body="Ihr Paket wurde zugestellt.",
        )
        result = self.parser.parse_email(raw)
        assert result is not None
        assert result["status"] == "delivered"

    def test_german_out_for_delivery(self):
        """Test detection of German out-for-delivery status."""
        raw = _make_email(
            from_addr="order-update@amazon.de",
            subject="Zustellung heute: Bestellung 123-4567890-1234567",
            body="Ihr Paket wird heute zugestellt.",
        )
        result = self.parser.parse_email(raw)
        assert result is not None
        assert result["status"] == "out_for_delivery"

    def test_german_carrier_dhl(self):
        """Test DHL carrier detection in German email."""
        raw = _make_email(
            from_addr="order-update@amazon.de",
            subject="Versandt: Bestellung 123-4567890-1234567",
            body="Ihr Paket wurde mit DHL Trackingnummer 123456789012 versandt.",
        )
        result = self.parser.parse_email(raw)
        assert result is not None
        assert result["carrier"] == "DHL"

    def test_german_carrier_hermes(self):
        """Test Hermes carrier detection in German email."""
        raw = _make_email(
            from_addr="order-update@amazon.de",
            subject="Versandt: Bestellung 123-4567890-1234567",
            body="Ihr Paket wurde durch Hermes versandt.",
        )
        result = self.parser.parse_email(raw)
        assert result is not None
        assert result["carrier"] == "Hermes"

    # --- English email tests ---

    def test_english_shipped_status(self):
        """Test detection of English shipped status."""
        raw = _make_email(
            from_addr="order-update@amazon.com",
            subject="Shipped: Your Order 123-4567890-1234567",
            body="Your package has been shipped with UPS.",
        )
        result = self.parser.parse_email(raw)
        assert result is not None
        assert result["status"] == "shipped"

    def test_english_delivered_status(self):
        """Test detection of English delivered status."""
        raw = _make_email(
            from_addr="order-update@amazon.com",
            subject="Delivered: Order 123-4567890-1234567",
            body="Your package has been delivered.",
        )
        result = self.parser.parse_email(raw)
        assert result is not None
        assert result["status"] == "delivered"

    def test_english_carrier_ups(self):
        """Test UPS carrier detection in English email."""
        raw = _make_email(
            from_addr="order-update@amazon.com",
            subject="Shipped: Order 123-4567890-1234567",
            body="Your package was shipped with UPS Tracking ID 1Z999AA10123456784.",
        )
        result = self.parser.parse_email(raw)
        assert result is not None
        assert result["carrier"] == "UPS"

    # --- French email tests ---

    def test_french_shipped_status(self):
        """Test detection of French shipped status."""
        raw = _make_email(
            from_addr="order-update@amazon.fr",
            subject="Expédié: Commande 123-4567890-1234567",
            body="Votre colis a été expédié.",
        )
        result = self.parser.parse_email(raw)
        assert result is not None
        assert result["status"] == "shipped"

    def test_french_delivered_status(self):
        """Test detection of French delivered status."""
        raw = _make_email(
            from_addr="order-update@amazon.fr",
            subject="Livré: Commande 123-4567890-1234567",
            body="Votre colis a été livré.",
        )
        result = self.parser.parse_email(raw)
        assert result is not None
        assert result["status"] == "delivered"

    # --- Tracking number extraction ---

    def test_tracking_number_dhl(self):
        """Test DHL tracking number extraction."""
        raw = _make_email(
            from_addr="order-update@amazon.de",
            subject="Versandt: Bestellung 123-4567890-1234567",
            body="Versandt mit DHL Trackingnummer: 123456789012",
        )
        result = self.parser.parse_email(raw)
        assert result is not None
        assert result["tracking_number"] == "123456789012"

    def test_tracking_number_amazon_logistics(self):
        """Test Amazon Logistics tracking number extraction."""
        raw = _make_email(
            from_addr="order-update@amazon.de",
            subject="Versandt: Bestellung 123-4567890-1234567",
            body="Versandt mit Amazon Logistics Trackingnummer TBA123456789012",
        )
        result = self.parser.parse_email(raw)
        assert result is not None
        assert result["carrier"] == "Amazon Logistics"

    def test_order_number_in_body(self):
        """Test order number extraction from body when not in subject."""
        raw = _make_email(
            from_addr="order-update@amazon.de",
            subject="Versandt: Ihre Amazon-Bestellung",
            body="Bestellnummer: 123-4567890-1234567\nIhr Paket wurde versandt.",
        )
        result = self.parser.parse_email(raw)
        assert result is not None
        assert result["order_number"] == "123-4567890-1234567"

    # --- HTML email tests ---

    def test_html_email_parsing(self):
        """Test that HTML emails are parsed correctly."""
        html_body = """
        <html><body>
        <p>Ihre Bestellung 123-4567890-1234567 wurde mit DHL versandt.</p>
        <p>Trackingnummer: 123456789012</p>
        </body></html>
        """
        raw = _make_email(
            from_addr="order-update@amazon.de",
            subject="Versandt: Bestellung 123-4567890-1234567",
            body=html_body,
            content_type="text/html",
        )
        result = self.parser.parse_email(raw)
        assert result is not None
        assert result["order_number"] == "123-4567890-1234567"

    # --- Delivery date extraction ---

    def test_german_delivery_date(self):
        """Test German delivery date extraction."""
        raw = _make_email(
            from_addr="order-update@amazon.de",
            subject="Versandt: Bestellung 123-4567890-1234567",
            body="Lieferung am 15.03.2025",
        )
        result = self.parser.parse_email(raw)
        assert result is not None
        assert result["estimated_delivery"] == "2025-03-15"

    def test_unconfigured_domain_ignored(self):
        """Test that emails from unconfigured domains are ignored."""
        parser = AmazonEmailParser(["amazon.de"])
        raw = _make_email(
            from_addr="order-update@amazon.com",
            subject="Shipped: Order 123-4567890-1234567",
            body="Your package shipped.",
        )
        result = parser.parse_email(raw)
        assert result is None


class TestBuildImapSearchQuery:
    """Test IMAP search query building."""

    def test_single_domain(self):
        """Test query with single domain."""
        query = build_imap_search_query(["amazon.de"], date(2025, 1, 1))
        assert "order-update@amazon.de" in query
        assert "SINCE" in query

    def test_multiple_domains(self):
        """Test query with multiple domains."""
        query = build_imap_search_query(
            ["amazon.de", "amazon.com"], date(2025, 1, 1)
        )
        assert "order-update@amazon.de" in query
        assert "order-update@amazon.com" in query
        assert "OR" in query

    def test_since_date_format(self):
        """Test that the SINCE date is formatted correctly."""
        query = build_imap_search_query(["amazon.de"], date(2025, 2, 15))
        assert "15-Feb-2025" in query

    def test_unknown_domain_ignored(self):
        """Test that unknown domains are silently ignored."""
        query = build_imap_search_query(["amazon.invalid"], date(2025, 1, 1))
        assert "SINCE" in query
