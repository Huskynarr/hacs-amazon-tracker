"""Sensor platform for Amazon Package Tracker."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTR_CARRIER,
    ATTR_ESTIMATED_DELIVERY,
    ATTR_LAST_UPDATED,
    ATTR_ORDER_DATE,
    ATTR_ORDER_NUMBER,
    ATTR_PRODUCT_NAME,
    ATTR_STATUS,
    ATTR_TRACKING_NUMBER,
    DOMAIN,
    STATUS_DELIVERED,
)
from .coordinator import AmazonTrackerCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Amazon Package Tracker sensors."""
    coordinator: AmazonTrackerCoordinator = hass.data[DOMAIN][entry.entry_id]

    # Track which order numbers already have entities
    tracked_orders: set[str] = set()

    # Add pending packages sensor
    async_add_entities([PendingPackagesSensor(coordinator, entry)])

    @callback
    def _async_add_new_sensors() -> None:
        """Add sensors for new packages."""
        if coordinator.data is None:
            return

        new_entities = []
        for order_number in coordinator.data:
            if order_number not in tracked_orders:
                tracked_orders.add(order_number)
                new_entities.append(
                    AmazonPackageSensor(coordinator, entry, order_number)
                )

        if new_entities:
            async_add_entities(new_entities)
            _LOGGER.debug("Added %d new package sensors", len(new_entities))

    # Add sensors for existing packages
    _async_add_new_sensors()

    # Listen for coordinator updates to add new package sensors
    entry.async_on_unload(
        coordinator.async_add_listener(_async_add_new_sensors)
    )


class AmazonPackageSensor(CoordinatorEntity, SensorEntity):
    """Sensor for an individual Amazon package."""

    def __init__(
        self,
        coordinator: AmazonTrackerCoordinator,
        entry: ConfigEntry,
        order_number: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._order_number = order_number
        self._attr_name = f"Amazon Package {order_number}"
        self._attr_unique_id = f"{DOMAIN}_{entry.entry_id}_{order_number}"
        self._attr_icon = "mdi:package-variant"

    @property
    def _package_data(self) -> dict[str, Any] | None:
        """Get current package data from coordinator."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get(self._order_number)

    @property
    def native_value(self) -> str | None:
        """Return the package status."""
        pkg = self._package_data
        return pkg.get(ATTR_STATUS) if pkg else None

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.last_update_success and self._package_data is not None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        pkg = self._package_data
        if not pkg:
            return {}

        return {
            ATTR_TRACKING_NUMBER: pkg.get(ATTR_TRACKING_NUMBER),
            ATTR_CARRIER: pkg.get(ATTR_CARRIER),
            ATTR_ESTIMATED_DELIVERY: pkg.get(ATTR_ESTIMATED_DELIVERY),
            ATTR_ORDER_DATE: pkg.get(ATTR_ORDER_DATE),
            ATTR_ORDER_NUMBER: self._order_number,
            ATTR_PRODUCT_NAME: pkg.get(ATTR_PRODUCT_NAME),
            ATTR_LAST_UPDATED: pkg.get(ATTR_LAST_UPDATED),
        }


class PendingPackagesSensor(CoordinatorEntity, SensorEntity):
    """Sensor showing the number of pending (non-delivered) packages."""

    def __init__(
        self,
        coordinator: AmazonTrackerCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = "Amazon Pending Packages"
        self._attr_unique_id = f"{DOMAIN}_{entry.entry_id}_pending_packages"
        self._attr_icon = "mdi:package-variant-closed"

    @property
    def native_value(self) -> int:
        """Return the number of pending packages."""
        if self.coordinator.data is None:
            return 0
        return len(
            [
                p
                for p in self.coordinator.data.values()
                if p.get(ATTR_STATUS) != STATUS_DELIVERED
            ]
        )

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        if self.coordinator.data is None:
            return {"packages": []}

        pending = [
            p
            for p in self.coordinator.data.values()
            if p.get(ATTR_STATUS) != STATUS_DELIVERED
        ]

        # Sort by estimated delivery date (None last)
        pending.sort(
            key=lambda x: x.get(ATTR_ESTIMATED_DELIVERY) or "9999-99-99"
        )

        return {
            "packages": [
                {
                    ATTR_PRODUCT_NAME: p.get(ATTR_PRODUCT_NAME),
                    ATTR_CARRIER: p.get(ATTR_CARRIER),
                    ATTR_STATUS: p.get(ATTR_STATUS),
                    ATTR_ESTIMATED_DELIVERY: p.get(ATTR_ESTIMATED_DELIVERY),
                    ATTR_TRACKING_NUMBER: p.get(ATTR_TRACKING_NUMBER),
                    ATTR_ORDER_NUMBER: p.get(ATTR_ORDER_NUMBER),
                }
                for p in pending
            ]
        }
