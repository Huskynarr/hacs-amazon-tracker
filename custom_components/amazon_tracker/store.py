"""Persistent storage for Amazon package data."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

from .const import (
    STORAGE_KEY,
    STORAGE_VERSION,
    STATUS_PRIORITY,
)

_LOGGER = logging.getLogger(__name__)


class PackageStore:
    """Persistent storage for package data using HA Store."""

    def __init__(self, hass: HomeAssistant, entry_id: str) -> None:
        """Initialize the package store."""
        self._store = Store(
            hass,
            STORAGE_VERSION,
            f"{STORAGE_KEY}_{entry_id}",
        )
        self._packages: dict[str, dict[str, Any]] = {}

    async def async_load(self) -> None:
        """Load packages from persistent storage."""
        data = await self._store.async_load()
        if data and isinstance(data, dict):
            self._packages = data.get("packages", {})
        _LOGGER.debug("Loaded %d packages from storage", len(self._packages))

    async def async_save(self) -> None:
        """Save packages to persistent storage."""
        await self._store.async_save({"packages": self._packages})

    @property
    def packages(self) -> dict[str, dict[str, Any]]:
        """Return all stored packages."""
        return self._packages

    def merge_packages(self, new_packages: list[dict[str, Any]]) -> list[str]:
        """Merge new package data into the store.

        Deduplicates by order number.
        Status only moves forward (ordered→shipped→delivered, never backwards).

        Returns list of order numbers that were added or updated.
        """
        changed: list[str] = []

        for pkg in new_packages:
            order_number = pkg.get("order_number")
            if not order_number:
                continue

            existing = self._packages.get(order_number)
            if existing is None:
                # New package
                self._packages[order_number] = pkg
                changed.append(order_number)
                _LOGGER.debug("New package: %s", order_number)
            else:
                # Update existing - merge fields, status only forward
                updated = False

                new_status = pkg.get("status")
                old_status = existing.get("status")
                if new_status and old_status:
                    new_priority = STATUS_PRIORITY.get(new_status, 0)
                    old_priority = STATUS_PRIORITY.get(old_status, 0)
                    if new_priority > old_priority:
                        existing["status"] = new_status
                        updated = True

                # Update fields if they are newly available
                for field in [
                    "carrier",
                    "tracking_number",
                    "estimated_delivery",
                    "product_name",
                ]:
                    if pkg.get(field) and not existing.get(field):
                        existing[field] = pkg[field]
                        updated = True

                # Always update last_updated
                if pkg.get("last_updated"):
                    existing["last_updated"] = pkg["last_updated"]
                    updated = True

                if updated:
                    changed.append(order_number)
                    _LOGGER.debug("Updated package: %s", order_number)

        return changed

    def get_active_packages(
        self,
        tracking_duration: int = 14,
        show_delivered: bool = True,
        delivered_duration: int = 3,
    ) -> dict[str, dict[str, Any]]:
        """Get filtered list of active packages.

        Args:
            tracking_duration: Max age in days to track packages.
            show_delivered: Whether to include delivered packages.
            delivered_duration: How long to show delivered packages (days).
        """
        now = datetime.now()
        result: dict[str, dict[str, Any]] = {}

        for order_number, pkg in self._packages.items():
            last_updated_str = pkg.get("last_updated", "")
            try:
                last_updated = datetime.fromisoformat(last_updated_str)
            except (ValueError, TypeError):
                last_updated = now

            age = now - last_updated

            # Skip packages older than tracking duration
            if age > timedelta(days=tracking_duration):
                continue

            # Handle delivered packages
            if pkg.get("status") == "delivered":
                if not show_delivered:
                    continue
                if age > timedelta(days=delivered_duration):
                    continue

            result[order_number] = pkg

        return result

    def cleanup_old_packages(self, max_age_days: int = 30) -> int:
        """Remove packages older than max_age_days.

        Returns number of removed packages.
        """
        now = datetime.now()
        to_remove: list[str] = []

        for order_number, pkg in self._packages.items():
            last_updated_str = pkg.get("last_updated", "")
            try:
                last_updated = datetime.fromisoformat(last_updated_str)
            except (ValueError, TypeError):
                last_updated = now

            if now - last_updated > timedelta(days=max_age_days):
                to_remove.append(order_number)

        for order_number in to_remove:
            del self._packages[order_number]

        if to_remove:
            _LOGGER.debug("Cleaned up %d old packages", len(to_remove))

        return len(to_remove)
