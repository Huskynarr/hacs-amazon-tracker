"""Tests for the Amazon Tracker sensor platform."""
import pytest
from unittest.mock import MagicMock

from custom_components.amazon_tracker.const import (
    ATTR_CARRIER,
    ATTR_ESTIMATED_DELIVERY,
    ATTR_ORDER_NUMBER,
    ATTR_PRODUCT_NAME,
    ATTR_STATUS,
    ATTR_TRACKING_NUMBER,
    DOMAIN,
    STATUS_DELIVERED,
    STATUS_SHIPPED,
    STATUS_ORDERED,
)
from custom_components.amazon_tracker.sensor import (
    AmazonPackageSensor,
    PendingPackagesSensor,
)


@pytest.fixture
def coordinator():
    """Create a mock coordinator with package data."""
    coord = MagicMock()
    coord.data = {
        "111-2222222-3333333": {
            ATTR_STATUS: STATUS_SHIPPED,
            ATTR_CARRIER: "DHL",
            ATTR_TRACKING_NUMBER: "123456789012",
            ATTR_ESTIMATED_DELIVERY: "2026-01-15",
            ATTR_ORDER_NUMBER: "111-2222222-3333333",
            ATTR_PRODUCT_NAME: "Test Product",
            "last_updated": "2026-01-10T10:00:00",
            "order_date": "2026-01-08T10:00:00",
        },
        "444-5555555-6666666": {
            ATTR_STATUS: STATUS_DELIVERED,
            ATTR_CARRIER: "UPS",
            ATTR_TRACKING_NUMBER: "1Z1234567890",
            ATTR_ESTIMATED_DELIVERY: "2026-01-12",
            ATTR_ORDER_NUMBER: "444-5555555-6666666",
            ATTR_PRODUCT_NAME: "Delivered Item",
            "last_updated": "2026-01-12T14:00:00",
            "order_date": "2026-01-05T10:00:00",
        },
    }
    coord.last_update_success = True
    return coord


@pytest.fixture
def entry():
    """Create a mock config entry."""
    e = MagicMock()
    e.entry_id = "test_entry"
    return e


class TestAmazonPackageSensor:
    """Test individual package sensor."""

    def test_sensor_name(self, coordinator, entry):
        sensor = AmazonPackageSensor(coordinator, entry, "111-2222222-3333333")
        assert sensor._attr_name == "Amazon Package 111-2222222-3333333"

    def test_sensor_unique_id(self, coordinator, entry):
        sensor = AmazonPackageSensor(coordinator, entry, "111-2222222-3333333")
        assert sensor._attr_unique_id == "amazon_tracker_test_entry_111-2222222-3333333"

    def test_sensor_native_value(self, coordinator, entry):
        sensor = AmazonPackageSensor(coordinator, entry, "111-2222222-3333333")
        assert sensor.native_value == STATUS_SHIPPED

    def test_sensor_available(self, coordinator, entry):
        sensor = AmazonPackageSensor(coordinator, entry, "111-2222222-3333333")
        assert sensor.available is True

    def test_sensor_not_available_for_missing(self, coordinator, entry):
        sensor = AmazonPackageSensor(coordinator, entry, "nonexistent")
        assert sensor.available is False

    def test_sensor_extra_state_attributes(self, coordinator, entry):
        sensor = AmazonPackageSensor(coordinator, entry, "111-2222222-3333333")
        attrs = sensor.extra_state_attributes
        assert attrs[ATTR_CARRIER] == "DHL"
        assert attrs[ATTR_TRACKING_NUMBER] == "123456789012"
        assert attrs[ATTR_ESTIMATED_DELIVERY] == "2026-01-15"
        assert attrs[ATTR_ORDER_NUMBER] == "111-2222222-3333333"
        assert attrs[ATTR_PRODUCT_NAME] == "Test Product"

    def test_sensor_extra_state_attributes_empty(self, coordinator, entry):
        sensor = AmazonPackageSensor(coordinator, entry, "nonexistent")
        assert sensor.extra_state_attributes == {}


class TestPendingPackagesSensor:
    """Test pending packages aggregate sensor."""

    def test_sensor_name(self, coordinator, entry):
        sensor = PendingPackagesSensor(coordinator, entry)
        assert sensor._attr_name == "Amazon Pending Packages"

    def test_sensor_unique_id(self, coordinator, entry):
        sensor = PendingPackagesSensor(coordinator, entry)
        assert sensor._attr_unique_id == "amazon_tracker_test_entry_pending_packages"

    def test_sensor_native_value_counts_non_delivered(self, coordinator, entry):
        sensor = PendingPackagesSensor(coordinator, entry)
        assert sensor.native_value == 1

    def test_sensor_native_value_zero_when_none(self, entry):
        coord = MagicMock()
        coord.data = None
        coord.last_update_success = True
        sensor = PendingPackagesSensor(coord, entry)
        assert sensor.native_value == 0

    def test_sensor_packages_attr(self, coordinator, entry):
        sensor = PendingPackagesSensor(coordinator, entry)
        attrs = sensor.extra_state_attributes
        assert "packages" in attrs
        assert len(attrs["packages"]) == 1
        pkg = attrs["packages"][0]
        assert pkg[ATTR_ORDER_NUMBER] == "111-2222222-3333333"

    def test_sensor_packages_attr_empty(self, entry):
        coord = MagicMock()
        coord.data = None
        coord.last_update_success = True
        sensor = PendingPackagesSensor(coord, entry)
        attrs = sensor.extra_state_attributes
        assert attrs == {"packages": []}

    def test_sensor_packages_sorted_by_delivery(self, entry):
        coord = MagicMock()
        coord.data = {
            "AAA-1111111-1111111": {
                ATTR_STATUS: STATUS_ORDERED,
                ATTR_ESTIMATED_DELIVERY: "2026-03-01",
                ATTR_ORDER_NUMBER: "AAA-1111111-1111111",
            },
            "BBB-2222222-2222222": {
                ATTR_STATUS: STATUS_SHIPPED,
                ATTR_ESTIMATED_DELIVERY: "2026-01-01",
                ATTR_ORDER_NUMBER: "BBB-2222222-2222222",
            },
        }
        coord.last_update_success = True
        sensor = PendingPackagesSensor(coord, entry)
        attrs = sensor.extra_state_attributes
        assert attrs["packages"][0][ATTR_ORDER_NUMBER] == "BBB-2222222-2222222"
        assert attrs["packages"][1][ATTR_ORDER_NUMBER] == "AAA-1111111-1111111"

    def test_sensor_packages_none_delivery_sorts_last(self, entry):
        coord = MagicMock()
        coord.data = {
            "AAA-1111111-1111111": {
                ATTR_STATUS: STATUS_ORDERED,
                ATTR_ESTIMATED_DELIVERY: None,
                ATTR_ORDER_NUMBER: "AAA-1111111-1111111",
            },
            "BBB-2222222-2222222": {
                ATTR_STATUS: STATUS_SHIPPED,
                ATTR_ESTIMATED_DELIVERY: "2026-01-01",
                ATTR_ORDER_NUMBER: "BBB-2222222-2222222",
            },
        }
        coord.last_update_success = True
        sensor = PendingPackagesSensor(coord, entry)
        attrs = sensor.extra_state_attributes
        assert attrs["packages"][-1][ATTR_ORDER_NUMBER] == "AAA-1111111-1111111"
