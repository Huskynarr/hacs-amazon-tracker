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
    ATTR_TRACKING_NUMBER,
    ATTR_CARRIER,
    ATTR_ESTIMATED_DELIVERY,
    ATTR_ORDER_DATE,
    ATTR_ORDER_NUMBER,
    ATTR_PRODUCT_NAME,
    ATTR_STATUS,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Amazon Package Tracker sensor."""
    coordinator = AmazonTrackerCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    async_add_entities(
        AmazonPackageSensor(coordinator, package)
        for package in coordinator.data
    )

class AmazonTrackerCoordinator(DataUpdateCoordinator):
    """My Amazon Package Tracker coordinator."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize my coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="Amazon Package Tracker",
            update_interval=entry.data.get("scan_interval"),
        )
        self.entry = entry

    async def _async_update_data(self) -> list[dict[str, Any]]:
        """Fetch data from Amazon."""
        # Here you would implement the actual Amazon API call
        # For now, we'll return dummy data
        return [
            {
                ATTR_TRACKING_NUMBER: "123456789",
                ATTR_CARRIER: "DHL",
                ATTR_ESTIMATED_DELIVERY: datetime.now().isoformat(),
                ATTR_ORDER_DATE: datetime.now().isoformat(),
                ATTR_ORDER_NUMBER: "ORDER123",
                ATTR_PRODUCT_NAME: "Test Product",
                ATTR_STATUS: "In Transit",
            }
        ]

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