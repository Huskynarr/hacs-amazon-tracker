"""Tests for Amazon domain configuration constants."""
import pytest
from custom_components.amazon_tracker.const import (
    AMAZON_DOMAINS,
    CONF_DOMAIN,
    DEFAULT_DOMAIN,
)


class TestAmazonDomains:
    """Test Amazon domain configurations."""

    def test_amazon_domains_structure(self):
        """Test that AMAZON_DOMAINS has the correct structure."""
        assert isinstance(AMAZON_DOMAINS, dict)
        assert len(AMAZON_DOMAINS) == 5
        
        # Check all expected domains are present
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
        required_keys = ["name", "base_url", "language"]
        
        for domain, config in AMAZON_DOMAINS.items():
            assert isinstance(config, dict), f"Config for {domain} should be a dict"
            for key in required_keys:
                assert key in config, f"Missing {key} in {domain} config"

    def test_amazon_com_configuration(self):
        """Test Amazon.com configuration."""
        config = AMAZON_DOMAINS["amazon.com"]
        assert config["name"] == "Amazon.com (United States)"
        assert config["base_url"] == "https://www.amazon.com"
        assert config["language"] == "en"

    def test_amazon_de_configuration(self):
        """Test Amazon.de configuration."""
        config = AMAZON_DOMAINS["amazon.de"]
        assert config["name"] == "Amazon.de (Germany)"
        assert config["base_url"] == "https://www.amazon.de"
        assert config["language"] == "de"

    def test_amazon_fr_configuration(self):
        """Test Amazon.fr configuration."""
        config = AMAZON_DOMAINS["amazon.fr"]
        assert config["name"] == "Amazon.fr (France)"
        assert config["base_url"] == "https://www.amazon.fr"
        assert config["language"] == "fr"

    def test_amazon_co_uk_configuration(self):
        """Test Amazon.co.uk configuration."""
        config = AMAZON_DOMAINS["amazon.co.uk"]
        assert config["name"] == "Amazon.co.uk (United Kingdom)"
        assert config["base_url"] == "https://www.amazon.co.uk"
        assert config["language"] == "en"

    def test_amazon_ie_configuration(self):
        """Test Amazon.ie configuration."""
        config = AMAZON_DOMAINS["amazon.ie"]
        assert config["name"] == "Amazon.ie (Ireland)"
        assert config["base_url"] == "https://www.amazon.ie"
        assert config["language"] == "en"

    def test_default_domain(self):
        """Test that default domain is set correctly."""
        assert DEFAULT_DOMAIN == "amazon.de"
        assert DEFAULT_DOMAIN in AMAZON_DOMAINS

    def test_conf_domain_constant(self):
        """Test that CONF_DOMAIN constant is defined."""
        assert CONF_DOMAIN == "amazon_domain"

    def test_base_urls_are_https(self):
        """Test that all base URLs use HTTPS."""
        for domain, config in AMAZON_DOMAINS.items():
            assert config["base_url"].startswith("https://"), \
                f"{domain} should use HTTPS"

    def test_languages_are_valid(self):
        """Test that all languages are valid ISO codes."""
        valid_languages = ["en", "de", "fr", "es"]
        for domain, config in AMAZON_DOMAINS.items():
            assert config["language"] in valid_languages, \
                f"{domain} has invalid language code: {config['language']}"

