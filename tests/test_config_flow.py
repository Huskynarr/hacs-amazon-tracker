"""Tests for config flow."""
import pytest

from custom_components.amazon_tracker.const import (
    AMAZON_DOMAINS,
    CONF_AMAZON_DOMAINS,
    CONF_IMAP_EMAIL,
    CONF_IMAP_FOLDER,
    CONF_IMAP_PASSWORD,
    CONF_IMAP_PORT,
    CONF_IMAP_SERVER,
    CONF_IMAP_SSL,
    CONF_SHOW_DELIVERED,
    CONF_TRACKING_DURATION,
    CONF_DELIVERED_DURATION,
    DEFAULT_DOMAIN,
    DEFAULT_IMAP_FOLDER,
    DEFAULT_IMAP_PORT,
    DEFAULT_IMAP_SSL,
    DEFAULT_TRACKING_DURATION,
    DEFAULT_SHOW_DELIVERED,
    DEFAULT_DELIVERED_DURATION,
    DOMAIN,
)


class TestConfigFlowConstants:
    """Test that config flow constants are properly defined."""

    def test_imap_constants_defined(self):
        """Test IMAP configuration constants exist."""
        assert CONF_IMAP_SERVER == "imap_server"
        assert CONF_IMAP_PORT == "imap_port"
        assert CONF_IMAP_EMAIL == "imap_email"
        assert CONF_IMAP_PASSWORD == "imap_password"
        assert CONF_IMAP_SSL == "imap_ssl"
        assert CONF_IMAP_FOLDER == "imap_folder"

    def test_amazon_constants_defined(self):
        """Test Amazon configuration constants exist."""
        assert CONF_AMAZON_DOMAINS == "amazon_domains"
        assert CONF_TRACKING_DURATION == "tracking_duration"
        assert CONF_SHOW_DELIVERED == "show_delivered"
        assert CONF_DELIVERED_DURATION == "delivered_duration"

    def test_defaults(self):
        """Test default values are sensible."""
        assert DEFAULT_IMAP_PORT == 993
        assert DEFAULT_IMAP_SSL is True
        assert DEFAULT_IMAP_FOLDER == "INBOX"
        assert DEFAULT_TRACKING_DURATION == 14
        assert DEFAULT_SHOW_DELIVERED is True
        assert DEFAULT_DELIVERED_DURATION == 3

    def test_domain_constant(self):
        """Test domain constant."""
        assert DOMAIN == "amazon_tracker"

    def test_default_domain_is_valid(self):
        """Test that the default domain is valid."""
        assert DEFAULT_DOMAIN in AMAZON_DOMAINS

    def test_all_domains_have_names(self):
        """Test all domains have user-friendly names."""
        for domain, config in AMAZON_DOMAINS.items():
            assert "name" in config
            assert len(config["name"]) > 0

    def test_config_flow_module_imports(self):
        """Test that config flow module can be imported."""
        from custom_components.amazon_tracker.config_flow import ConfigFlow
        assert ConfigFlow is not None

    def test_config_flow_version_2(self):
        """Test config flow version is 2."""
        import os
        config_flow_path = os.path.join(
            os.path.dirname(__file__),
            "..", "custom_components", "amazon_tracker", "config_flow.py",
        )
        with open(config_flow_path) as f:
            source = f.read()
        assert "VERSION = 2" in source

    def test_options_flow_handler_exists(self):
        """Test that OptionsFlowHandler exists."""
        from custom_components.amazon_tracker.config_flow import OptionsFlowHandler
        assert OptionsFlowHandler is not None
