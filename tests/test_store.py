"""Tests for Amazon package store."""
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.amazon_tracker.store import PackageStore


def _make_package(
    order_number: str = "123-4567890-1234567",
    status: str = "shipped",
    carrier: str = "DHL",
    tracking_number: str = "123456789012",
    last_updated: str | None = None,
    product_name: str = "Test Product",
) -> dict:
    """Create a test package dict."""
    if last_updated is None:
        last_updated = datetime.now().isoformat()
    return {
        "order_number": order_number,
        "status": status,
        "carrier": carrier,
        "tracking_number": tracking_number,
        "estimated_delivery": "2025-03-15",
        "product_name": product_name,
        "last_updated": last_updated,
        "order_date": last_updated,
    }


class TestPackageStore:
    """Test PackageStore class."""

    def setup_method(self):
        """Set up test fixtures."""
        mock_hass = MagicMock()
        # Mock the Store class
        with patch("custom_components.amazon_tracker.store.Store"):
            self.store = PackageStore(mock_hass, "test_entry_id")

    def test_merge_new_package(self):
        """Test merging a new package."""
        pkg = _make_package(order_number="111-1111111-1111111")
        changed = self.store.merge_packages([pkg])
        assert "111-1111111-1111111" in changed
        assert "111-1111111-1111111" in self.store.packages

    def test_merge_duplicate_package(self):
        """Test that duplicate packages are merged, not duplicated."""
        pkg1 = _make_package(order_number="111-1111111-1111111", status="shipped")
        pkg2 = _make_package(order_number="111-1111111-1111111", status="shipped")
        self.store.merge_packages([pkg1])
        changed = self.store.merge_packages([pkg2])
        assert len(self.store.packages) == 1

    def test_status_progression_forward(self):
        """Test that status moves forward (shipped → delivered)."""
        pkg1 = _make_package(order_number="111-1111111-1111111", status="shipped")
        pkg2 = _make_package(order_number="111-1111111-1111111", status="delivered")
        self.store.merge_packages([pkg1])
        changed = self.store.merge_packages([pkg2])
        assert "111-1111111-1111111" in changed
        assert self.store.packages["111-1111111-1111111"]["status"] == "delivered"

    def test_status_no_backward_progression(self):
        """Test that status does not go backwards (delivered → shipped)."""
        pkg1 = _make_package(order_number="111-1111111-1111111", status="delivered")
        pkg2 = _make_package(order_number="111-1111111-1111111", status="shipped")
        self.store.merge_packages([pkg1])
        self.store.merge_packages([pkg2])
        assert self.store.packages["111-1111111-1111111"]["status"] == "delivered"

    def test_merge_fills_missing_fields(self):
        """Test that merge fills in previously missing fields."""
        pkg1 = _make_package(
            order_number="111-1111111-1111111",
            carrier=None,
            tracking_number=None,
        )
        pkg1["carrier"] = None
        pkg1["tracking_number"] = None
        self.store.merge_packages([pkg1])

        pkg2 = _make_package(
            order_number="111-1111111-1111111",
            carrier="DHL",
            tracking_number="123456789012",
        )
        changed = self.store.merge_packages([pkg2])
        assert "111-1111111-1111111" in changed
        assert self.store.packages["111-1111111-1111111"]["carrier"] == "DHL"
        assert self.store.packages["111-1111111-1111111"]["tracking_number"] == "123456789012"

    def test_merge_does_not_overwrite_existing_fields(self):
        """Test that merge does not overwrite existing non-empty fields."""
        pkg1 = _make_package(
            order_number="111-1111111-1111111",
            carrier="DHL",
        )
        self.store.merge_packages([pkg1])

        pkg2 = _make_package(
            order_number="111-1111111-1111111",
            carrier="UPS",
        )
        self.store.merge_packages([pkg2])
        # Carrier should stay DHL (first known value)
        assert self.store.packages["111-1111111-1111111"]["carrier"] == "DHL"

    def test_skip_package_without_order_number(self):
        """Test that packages without order numbers are skipped."""
        pkg = _make_package()
        pkg["order_number"] = None
        changed = self.store.merge_packages([pkg])
        assert len(changed) == 0
        assert len(self.store.packages) == 0

    def test_get_active_packages_excludes_old(self):
        """Test that old packages are excluded."""
        old_date = (datetime.now() - timedelta(days=30)).isoformat()
        pkg = _make_package(order_number="111-1111111-1111111", last_updated=old_date)
        self.store.merge_packages([pkg])

        active = self.store.get_active_packages(tracking_duration=14)
        assert len(active) == 0

    def test_get_active_packages_includes_recent(self):
        """Test that recent packages are included."""
        recent_date = datetime.now().isoformat()
        pkg = _make_package(order_number="111-1111111-1111111", last_updated=recent_date)
        self.store.merge_packages([pkg])

        active = self.store.get_active_packages(tracking_duration=14)
        assert len(active) == 1

    def test_get_active_packages_hides_delivered(self):
        """Test that delivered packages are hidden when show_delivered=False."""
        pkg = _make_package(
            order_number="111-1111111-1111111",
            status="delivered",
        )
        self.store.merge_packages([pkg])

        active = self.store.get_active_packages(show_delivered=False)
        assert len(active) == 0

    def test_get_active_packages_shows_delivered(self):
        """Test that delivered packages are shown when show_delivered=True."""
        pkg = _make_package(
            order_number="111-1111111-1111111",
            status="delivered",
        )
        self.store.merge_packages([pkg])

        active = self.store.get_active_packages(show_delivered=True, delivered_duration=7)
        assert len(active) == 1

    def test_get_active_packages_hides_old_delivered(self):
        """Test that old delivered packages are hidden."""
        old_date = (datetime.now() - timedelta(days=10)).isoformat()
        pkg = _make_package(
            order_number="111-1111111-1111111",
            status="delivered",
            last_updated=old_date,
        )
        self.store.merge_packages([pkg])

        active = self.store.get_active_packages(
            show_delivered=True, delivered_duration=3
        )
        assert len(active) == 0

    def test_cleanup_old_packages(self):
        """Test cleanup of old packages."""
        old_date = (datetime.now() - timedelta(days=60)).isoformat()
        recent_date = datetime.now().isoformat()

        self.store.merge_packages([
            _make_package(order_number="111-1111111-1111111", last_updated=old_date),
            _make_package(order_number="222-2222222-2222222", last_updated=recent_date),
        ])

        removed = self.store.cleanup_old_packages(max_age_days=30)
        assert removed == 1
        assert "222-2222222-2222222" in self.store.packages
        assert "111-1111111-1111111" not in self.store.packages

    def test_multiple_packages(self):
        """Test handling multiple packages."""
        packages = [
            _make_package(order_number=f"{i:03d}-{i:07d}-{i:07d}")
            for i in range(1, 6)
        ]
        self.store.merge_packages(packages)
        assert len(self.store.packages) == 5
