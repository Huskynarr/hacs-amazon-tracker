"""Sensor platform for Amazon Package Tracker."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import (
    DOMAIN,
    CONF_DOMAIN,
    DEFAULT_DOMAIN,
    ATTR_TRACKING_NUMBER,
    ATTR_CARRIER,
    ATTR_ESTIMATED_DELIVERY,
    ATTR_ORDER_DATE,
    ATTR_ORDER_NUMBER,
    ATTR_PRODUCT_NAME,
    ATTR_STATUS,
    DEFAULT_SCAN_INTERVAL,
)
from .amazon_tracker import fetch_amazon_packages

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Amazon Package Tracker sensor."""
    try:
        coordinator = AmazonTrackerCoordinator(hass, entry)
        await coordinator.async_config_entry_first_refresh()

        # Add individual package sensors
        async_add_entities(
            AmazonPackageSensor(coordinator, package)
            for package in coordinator.data
        )

        # Add pending packages sensor
        async_add_entities([PendingPackagesSensor(coordinator)])
    except Exception as err:
        _LOGGER.error("Error setting up Amazon Package Tracker: %s", err)
        return False

class AmazonTrackerCoordinator(DataUpdateCoordinator):
    """My Amazon Package Tracker coordinator."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize my coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="Amazon Package Tracker",
            update_interval=entry.data.get("scan_interval", DEFAULT_SCAN_INTERVAL),
        )
        self.entry = entry
        self._email = entry.data.get("email")
        self._password = entry.data.get("password")
        self._domain = entry.data.get(CONF_DOMAIN, DEFAULT_DOMAIN)

    async def _async_update_data(self) -> list[dict[str, Any]]:
        """Fetch data from Amazon."""
        return await fetch_amazon_packages(self._email, self._password, self._domain)

class AmazonPackageSensor(CoordinatorEntity, SensorEntity):
    """Representation of an Amazon Package Tracker sensor."""

    def __init__(
        self, coordinator: AmazonTrackerCoordinator, package: dict[str, Any]
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.package = package
        self._attr_name = f"Amazon Package {package[ATTR_ORDER_NUMBER]}"
        self._attr_unique_id = f"{DOMAIN}_{package[ATTR_ORDER_NUMBER]}"
        self._attr_native_value = package[ATTR_STATUS]

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        return {
            ATTR_TRACKING_NUMBER: self.package[ATTR_TRACKING_NUMBER],
            ATTR_CARRIER: self.package[ATTR_CARRIER],
            ATTR_ESTIMATED_DELIVERY: self.package[ATTR_ESTIMATED_DELIVERY],
            ATTR_ORDER_DATE: self.package[ATTR_ORDER_DATE],
            ATTR_ORDER_NUMBER: self.package[ATTR_ORDER_NUMBER],
            ATTR_PRODUCT_NAME: self.package[ATTR_PRODUCT_NAME],
        }

class PendingPackagesSensor(CoordinatorEntity, SensorEntity):
    """Representation of pending Amazon packages."""

    def __init__(self, coordinator: AmazonTrackerCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = "Amazon Pending Packages"
        self._attr_unique_id = f"{DOMAIN}_pending_packages"
        self._attr_icon = "mdi:package-variant"

    @property
    def native_value(self) -> str:
        """Return the number of pending packages."""
        pending = len([p for p in self.coordinator.data if p[ATTR_STATUS] != "Delivered"])
        return str(pending)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        pending_packages = [p for p in self.coordinator.data if p[ATTR_STATUS] != "Delivered"]
        # Sort by estimated delivery date
        pending_packages.sort(key=lambda x: x[ATTR_ESTIMATED_DELIVERY])
        
        return {
            "packages": [
                {
                    ATTR_PRODUCT_NAME: p[ATTR_PRODUCT_NAME],
                    ATTR_CARRIER: p[ATTR_CARRIER],
                    ATTR_STATUS: p[ATTR_STATUS],
                    ATTR_ESTIMATED_DELIVERY: p[ATTR_ESTIMATED_DELIVERY],
                    ATTR_TRACKING_NUMBER: p[ATTR_TRACKING_NUMBER],
                    ATTR_ORDER_NUMBER: p[ATTR_ORDER_NUMBER],
                }
                for p in pending_packages
            ]
        } 