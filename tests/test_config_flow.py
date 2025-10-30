"""Tests for the config flow."""
import pytest
from custom_components.amazon_tracker.const import (
    DOMAIN,
    CONF_DOMAIN,
    AMAZON_DOMAINS,
    DEFAULT_DOMAIN,
)


class TestConfigFlowIntegration:
    """Test the Amazon Package Tracker config flow integration."""

    def test_domain_constant_defined(self):
        """Test that CONF_DOMAIN constant is properly defined."""
        assert CONF_DOMAIN == "amazon_domain"

    def test_default_domain_is_valid(self):
        """Test that DEFAULT_DOMAIN is in AMAZON_DOMAINS."""
        assert DEFAULT_DOMAIN in AMAZON_DOMAINS

    def test_all_domains_have_names(self):
        """Test that all domains have user-friendly names for the selector."""
        for domain, config in AMAZON_DOMAINS.items():
            assert "name" in config
            assert len(config["name"]) > 0
            assert isinstance(config["name"], str)

    def test_config_flow_module_imports(self):
        """Test that config_flow module can be imported."""
        try:
            from custom_components.amazon_tracker import config_flow
            assert hasattr(config_flow, 'ConfigFlow')
            assert hasattr(config_flow, 'DOMAIN')
        except ImportError as e:
            pytest.fail(f"Failed to import config_flow: {e}")

    def test_config_flow_has_domain_support(self):
        """Test that config_flow imports domain-related constants."""
        from custom_components.amazon_tracker import config_flow
        assert hasattr(config_flow, 'CONF_DOMAIN')
        assert hasattr(config_flow, 'AMAZON_DOMAINS')
        assert hasattr(config_flow, 'DEFAULT_DOMAIN')


