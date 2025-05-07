"""Sensor platform for Amazon Package Tracker."""
from __future__ import annotations

import logging
import re
from datetime import datetime
from typing import Any
import aiohttp
from bs4 import BeautifulSoup

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
    DEFAULT_SCAN_INTERVAL,
)

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
        self._session = None

    async def _async_update_data(self) -> list[dict[str, Any]]:
        """Fetch data from Amazon."""
        try:
            if not self._session:
                self._session = aiohttp.ClientSession()

            # First, get the order history page
            async with self._session.get("https://www.amazon.de/gp/css/order-history") as response:
                if response.status != 200:
                    raise Exception(f"Failed to get order history: {response.status}")
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Find all order cards
                order_cards = soup.find_all("li", class_="order-card__list")
                packages = []

                for card in order_cards:
                    try:
                        # Extract order number
                        order_number = card.find("span", class_="a-color-secondary", dir="ltr").text.strip()
                        
                        # Extract order date
                        order_date = card.find("span", class_="a-size-base a-color-secondary aok-break-word").text.strip()
                        
                        # Extract delivery status
                        delivery_status = card.find("span", class_="delivery-box__secondary-text").text.strip()
                        
                        # Extract estimated delivery
                        delivery_estimate = card.find("span", class_="delivery-box__primary-text").text.strip()
                        delivery_estimate = re.search(r"(\d{1,2}\.\s\w+\s-\s\d{1,2}\.\s\w+)", delivery_estimate).group(1)
                        
                        # Extract tracking link
                        tracking_link = card.find("a", href=lambda x: x and "ship-track" in x)
                        if tracking_link:
                            tracking_url = "https://www.amazon.de" + tracking_link['href']
                            
                            # Get tracking details
                            async with self._session.get(tracking_url) as tracking_response:
                                if tracking_response.status == 200:
                                    tracking_html = await tracking_response.text()
                                    tracking_soup = BeautifulSoup(tracking_html, 'html.parser')
                                    
                                    # Extract carrier and tracking number
                                    carrier_info = tracking_soup.find("div", class_="pt-delivery-card-trackingId")
                                    if carrier_info:
                                        carrier_text = carrier_info.text.strip()
                                        carrier = carrier_text.split(" mit ")[1].split("Trackingnummer")[0].strip()
                                        tracking_number = carrier_text.split("Trackingnummer")[1].strip()
                                        
                                        # Extract products
                                        products = []
                                        product_links = card.find_all("a", class_="a-link-normal", href=lambda x: x and "/dp/" in x)
                                        for product in product_links:
                                            products.append(product.text.strip())
                                        
                                        packages.append({
                                            ATTR_TRACKING_NUMBER: tracking_number,
                                            ATTR_CARRIER: carrier,
                                            ATTR_ESTIMATED_DELIVERY: delivery_estimate,
                                            ATTR_ORDER_DATE: order_date,
                                            ATTR_ORDER_NUMBER: order_number,
                                            ATTR_PRODUCT_NAME: ", ".join(products),
                                            ATTR_STATUS: delivery_status,
                                        })
                    except Exception as err:
                        _LOGGER.error("Error parsing order card: %s", err)
                        continue

                return packages

        except Exception as err:
            _LOGGER.error("Error fetching Amazon data: %s", err)
            return []

    async def async_close(self):
        """Close the session."""
        if self._session:
            await self._session.close()
            self._session = None

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