"""Tests for Amazon tracker constants."""
import pytest
from custom_components.amazon_tracker.const import (
    AMAZON_DOMAINS,
    CONF_AMAZON_DOMAINS,
    CONF_IMAP_EMAIL,
    CONF_IMAP_PASSWORD,
    CONF_IMAP_PORT,
    CONF_IMAP_SERVER,
    CONF_IMAP_SSL,
    CONF_IMAP_FOLDER,
    DEFAULT_DOMAIN,
    DEFAULT_IMAP_PORT,
    EMAIL_SUBJECTS,
    STATUS_PRIORITY,
    TRACKING_PATTERNS,
    CARRIER_PATTERNS,
    ORDER_NUMBER_PATTERN,
    STORAGE_KEY,
    STORAGE_VERSION,
)


class TestAmazonDomains:
    """Test Amazon domain configurations."""

    def test_amazon_domains_structure(self):
        """Test that AMAZON_DOMAINS has the correct structure."""
        assert isinstance(AMAZON_DOMAINS, dict)
        assert len(AMAZON_DOMAINS) >= 5

        expected_domains = [
            "amazon.com",
            "amazon.de",
            "amazon.fr",
            "amazon.co.uk",
            "amazon.ie",
        ]
        for domain in expected_domains:
            assert domain in AMAZON_DOMAINS

    def test_domain_configuration_keys(self):
        """Test that each domain has the required configuration keys."""
        required_keys = ["name", "sender", "language"]

        for domain, config in AMAZON_DOMAINS.items():
            assert isinstance(config, dict), f"Config for {domain} should be a dict"
            for key in required_keys:
                assert key in config, f"Missing {key} in {domain} config"

    def test_amazon_de_configuration(self):
        """Test Amazon.de configuration."""
        config = AMAZON_DOMAINS["amazon.de"]
        assert config["name"] == "Amazon.de (Germany)"
        assert config["sender"] == "order-update@amazon.de"
        assert config["language"] == "de"

    def test_amazon_com_configuration(self):
        """Test Amazon.com configuration."""
        config = AMAZON_DOMAINS["amazon.com"]
        assert config["name"] == "Amazon.com (United States)"
        assert config["sender"] == "order-update@amazon.com"
        assert config["language"] == "en"

    def test_default_domain(self):
        """Test that default domain is set correctly."""
        assert DEFAULT_DOMAIN == "amazon.de"
        assert DEFAULT_DOMAIN in AMAZON_DOMAINS

    def test_senders_match_domains(self):
        """Test that sender addresses match their domains."""
        for domain_key, config in AMAZON_DOMAINS.items():
            assert config["sender"].endswith(f"@{domain_key}"), \
                f"Sender for {domain_key} should end with @{domain_key}"


class TestIMAPConstants:
    """Test IMAP configuration constants."""

    def test_imap_conf_constants(self):
        """Test that IMAP configuration constants are defined."""
        assert CONF_IMAP_SERVER == "imap_server"
        assert CONF_IMAP_PORT == "imap_port"
        assert CONF_IMAP_EMAIL == "imap_email"
        assert CONF_IMAP_PASSWORD == "imap_password"
        assert CONF_IMAP_SSL == "imap_ssl"
        assert CONF_IMAP_FOLDER == "imap_folder"

    def test_default_imap_port(self):
        """Test default IMAP port."""
        assert DEFAULT_IMAP_PORT == 993


class TestStatusPriority:
    """Test status priority ordering."""

    def test_status_priority_order(self):
        """Test that status priorities are in correct order."""
        assert STATUS_PRIORITY["ordered"] < STATUS_PRIORITY["shipped"]
        assert STATUS_PRIORITY["shipped"] < STATUS_PRIORITY["out_for_delivery"]
        assert STATUS_PRIORITY["out_for_delivery"] < STATUS_PRIORITY["delivered"]

    def test_all_statuses_have_priority(self):
        """Test that all expected statuses have priority values."""
        expected = ["ordered", "shipped", "out_for_delivery", "delivered"]
        for status in expected:
            assert status in STATUS_PRIORITY


class TestEmailSubjects:
    """Test email subject patterns."""

    def test_all_statuses_have_patterns(self):
        """Test that all statuses have email subject patterns."""
        expected = ["shipped", "out_for_delivery", "delivered", "ordered"]
        for status in expected:
            assert status in EMAIL_SUBJECTS
            assert len(EMAIL_SUBJECTS[status]) > 0

    def test_shipped_patterns(self):
        """Test shipped status patterns include German and English."""
        patterns = EMAIL_SUBJECTS["shipped"]
        # Should have at least German and English patterns
        assert len(patterns) >= 2

    def test_delivered_patterns(self):
        """Test delivered status patterns."""
        patterns = EMAIL_SUBJECTS["delivered"]
        assert len(patterns) >= 2


class TestTrackingPatterns:
    """Test carrier tracking patterns."""

    def test_common_carriers_present(self):
        """Test that common carriers have tracking patterns."""
        expected_carriers = ["DHL", "DPD", "Hermes", "UPS", "Amazon Logistics"]
        for carrier in expected_carriers:
            assert carrier in TRACKING_PATTERNS, f"Missing patterns for {carrier}"

    def test_patterns_are_lists(self):
        """Test that patterns are lists of regex strings."""
        for carrier, patterns in TRACKING_PATTERNS.items():
            assert isinstance(patterns, list), f"Patterns for {carrier} should be a list"
            assert len(patterns) > 0, f"Patterns for {carrier} should not be empty"


class TestCarrierPatterns:
    """Test carrier detection patterns by language."""

    def test_languages_present(self):
        """Test that carrier patterns exist for major languages."""
        assert "de" in CARRIER_PATTERNS
        assert "en" in CARRIER_PATTERNS
        assert "fr" in CARRIER_PATTERNS


class TestStorageConstants:
    """Test storage constants."""

    def test_storage_key(self):
        """Test storage key."""
        assert "amazon_tracker" in STORAGE_KEY

    def test_storage_version(self):
        """Test storage version."""
        assert STORAGE_VERSION >= 1


class TestOrderNumberPattern:
    """Test order number regex pattern."""

    def test_pattern_matches_amazon_order(self):
        """Test that pattern matches Amazon order numbers."""
        import re
        pattern = ORDER_NUMBER_PATTERN
        assert re.search(pattern, "123-4567890-1234567")
        assert re.search(pattern, "Order 123-4567890-1234567 shipped")

    def test_pattern_rejects_invalid(self):
        """Test that pattern rejects non-order strings."""
        import re
        pattern = ORDER_NUMBER_PATTERN
        assert not re.search(pattern, "12345")
        assert not re.search(pattern, "abc-defghij-klmnopq")
