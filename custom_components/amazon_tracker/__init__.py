"""The Amazon Package Tracker integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall, callback

from .const import DOMAIN
from .coordinator import AmazonTrackerCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Amazon Package Tracker from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    coordinator = AmazonTrackerCoordinator(hass, entry)
    await coordinator.async_initialize()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    _register_services(hass)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        coordinator: AmazonTrackerCoordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.async_shutdown()

    if not hass.data[DOMAIN]:
        _unregister_services(hass)

    return unload_ok


@callback
def _register_services(hass: HomeAssistant) -> None:
    """Register domain services."""
    if hass.services.has_service(DOMAIN, "scan_now"):
        return

    async def _handle_scan_now(call: ServiceCall) -> None:
        """Handle the scan_now service — manually trigger an IMAP email scan."""
        entry_id = call.data.get("entry_id")
        coordinators = _get_coordinators(hass, entry_id)
        for coord in coordinators:
            await coord.async_scan_now()

    async def _handle_remove_package(call: ServiceCall) -> None:
        """Handle the remove_package service — remove a package from the store."""
        order_number = call.data.get("order_number")
        if not order_number:
            _LOGGER.warning("remove_package service called without order_number")
            return
        entry_id = call.data.get("entry_id")
        coordinators = _get_coordinators(hass, entry_id)
        for coord in coordinators:
            coord.remove_package(order_number)

    hass.services.async_register(DOMAIN, "scan_now", _handle_scan_now)
    hass.services.async_register(DOMAIN, "remove_package", _handle_remove_package)


@callback
def _unregister_services(hass: HomeAssistant) -> None:
    """Unregister domain services."""
    if hass.services.has_service(DOMAIN, "scan_now"):
        hass.services.async_remove(DOMAIN, "scan_now")
    if hass.services.has_service(DOMAIN, "remove_package"):
        hass.services.async_remove(DOMAIN, "remove_package")


def _get_coordinators(hass: HomeAssistant, entry_id: str | None) -> list[AmazonTrackerCoordinator]:
    """Get coordinator(s) by entry_id, or all if not specified."""
    domain_data: dict = hass.data.get(DOMAIN, {})
    if entry_id:
        coord = domain_data.get(entry_id)
        return [coord] if coord else []
    return list(domain_data.values())
