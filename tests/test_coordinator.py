"""Tests for the Amazon Tracker Coordinator."""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from custom_components.amazon_tracker.coordinator import AmazonTrackerCoordinator
from custom_components.amazon_tracker.const import (
    CONF_AMAZON_DOMAINS,
    CONF_TRACKING_DURATION,
    CONF_SHOW_DELIVERED,
    CONF_DELIVERED_DURATION,
    DEFAULT_TRACKING_DURATION,
    DEFAULT_SHOW_DELIVERED,
    DEFAULT_DELIVERED_DURATION,
)


@pytest.fixture
def coordinator():
    """Create a coordinator with mocked dependencies."""
    hass = MagicMock()
    entry = MagicMock()
    entry.entry_id = "test_entry"
    entry.options = {
        CONF_AMAZON_DOMAINS: ["amazon.de"],
        CONF_TRACKING_DURATION: 14,
        CONF_SHOW_DELIVERED: True,
        CONF_DELIVERED_DURATION: 3,
    }
    entry.data = {
        "imap_server": "imap.test.com",
        "imap_port": 993,
        "imap_email": "test@test.com",
        "imap_password": "pass",
        "imap_ssl": True,
        "imap_folder": "INBOX",
    }
    return AmazonTrackerCoordinator(hass, entry)


class TestCoordinatorInit:
    """Test coordinator initialization."""

    def test_coordinator_name(self, coordinator):
        assert coordinator.name == "amazon_tracker"

    def test_coordinator_has_store(self, coordinator):
        assert coordinator.store is not None

    def test_get_option_from_options(self, coordinator):
        assert coordinator._get_option(CONF_TRACKING_DURATION) == 14

    def test_get_option_fallback_to_data(self, coordinator):
        assert coordinator._get_option("imap_server") == "imap.test.com"

    def test_get_option_default(self, coordinator):
        assert coordinator._get_option("nonexistent", "fallback") == "fallback"


class TestRemovePackage:
    """Test remove_package service method."""

    def test_remove_existing_package(self, coordinator):
        coordinator._store._packages = {
            "123-4567890-1234567": {"status": "ordered"}
        }
        coordinator.hass = MagicMock()
        coordinator.remove_package("123-4567890-1234567")
        assert "123-4567890-1234567" not in coordinator.store.packages

    def test_remove_nonexistent_package(self, coordinator):
        coordinator._store._packages = {}
        coordinator.remove_package("nonexistent")
        assert len(coordinator.store.packages) == 0


class TestScanNow:
    """Test async_scan_now service method."""

    @pytest.mark.asyncio
    async def test_scan_now_not_connected(self, coordinator):
        coordinator._imap_client = MagicMock()
        coordinator._imap_client.is_connected = False
        await coordinator.async_scan_now()

    @pytest.mark.asyncio
    async def test_scan_no_client(self, coordinator):
        coordinator._imap_client = None
        await coordinator.async_scan_now()
