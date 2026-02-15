"""Data update coordinator for Amazon Package Tracker."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    CONF_AMAZON_DOMAINS,
    CONF_DELIVERED_DURATION,
    CONF_IMAP_EMAIL,
    CONF_IMAP_FOLDER,
    CONF_IMAP_PASSWORD,
    CONF_IMAP_PORT,
    CONF_IMAP_SERVER,
    CONF_IMAP_SSL,
    CONF_SHOW_DELIVERED,
    CONF_TRACKING_DURATION,
    DEFAULT_DELIVERED_DURATION,
    DEFAULT_IMAP_FOLDER,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_SHOW_DELIVERED,
    DEFAULT_TRACKING_DURATION,
    DOMAIN,
)
from .imap_client import ImapClient
from .store import PackageStore

_LOGGER = logging.getLogger(__name__)


class AmazonTrackerCoordinator(DataUpdateCoordinator):
    """Coordinator for Amazon Package Tracker."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=DEFAULT_SCAN_INTERVAL,
        )
        self._entry = entry
        self._store = PackageStore(hass, entry.entry_id)
        self._imap_client: ImapClient | None = None

    @property
    def store(self) -> PackageStore:
        """Return the package store."""
        return self._store

    def _get_option(self, key: str, default: Any = None) -> Any:
        """Get a config value from options (falling back to data)."""
        return self._entry.options.get(
            key, self._entry.data.get(key, default)
        )

    async def async_initialize(self) -> None:
        """Initialize the coordinator: load storage, connect IMAP, scan emails."""
        # Load stored packages
        await self._store.async_load()

        # Clean up old packages
        self._store.cleanup_old_packages(max_age_days=60)

        # Set up IMAP client
        domains = self._get_option(CONF_AMAZON_DOMAINS, [])
        if isinstance(domains, str):
            domains = [domains]

        self._imap_client = ImapClient(
            server=self._entry.data[CONF_IMAP_SERVER],
            port=self._entry.data[CONF_IMAP_PORT],
            email_addr=self._entry.data[CONF_IMAP_EMAIL],
            password=self._entry.data[CONF_IMAP_PASSWORD],
            ssl=self._entry.data.get(CONF_IMAP_SSL, True),
            folder=self._entry.data.get(CONF_IMAP_FOLDER, DEFAULT_IMAP_FOLDER),
            domains=domains,
            on_new_packages=self._handle_new_packages,
        )

        try:
            await self._imap_client.connect()

            # Scan existing emails
            tracking_duration = self._get_option(
                CONF_TRACKING_DURATION, DEFAULT_TRACKING_DURATION
            )
            existing = await self._imap_client.fetch_existing_emails(
                since_days=tracking_duration
            )
            if existing:
                self._store.merge_packages(existing)
                await self._store.async_save()

            # Start IDLE for push notifications
            await self._imap_client.start_idle()

        except Exception as err:
            _LOGGER.error("Failed to initialize IMAP: %s", err)
            # Continue without IMAP - will retry on next update

        # Set initial data
        self._update_data()

    async def async_shutdown(self) -> None:
        """Shut down the coordinator."""
        if self._imap_client:
            await self._imap_client.disconnect()
            self._imap_client = None

        await self._store.async_save()
        _LOGGER.debug("Coordinator shut down")

    def _handle_new_packages(self, packages: list[dict[str, Any]]) -> None:
        """Handle new packages from IMAP callback."""
        changed = self._store.merge_packages(packages)
        if changed:
            _LOGGER.info("Received %d new/updated packages via IMAP", len(changed))
            self._update_data()
            # Schedule save
            self.hass.async_create_task(self._store.async_save())

    def _update_data(self) -> None:
        """Update coordinator data from store."""
        tracking_duration = self._get_option(
            CONF_TRACKING_DURATION, DEFAULT_TRACKING_DURATION
        )
        show_delivered = self._get_option(
            CONF_SHOW_DELIVERED, DEFAULT_SHOW_DELIVERED
        )
        delivered_duration = self._get_option(
            CONF_DELIVERED_DURATION, DEFAULT_DELIVERED_DURATION
        )

        active = self._store.get_active_packages(
            tracking_duration=tracking_duration,
            show_delivered=show_delivered,
            delivered_duration=delivered_duration,
        )
        self.async_set_updated_data(active)

    async def _async_update_data(self) -> dict[str, Any]:
        """Fallback polling update (in case IDLE fails)."""
        if self._imap_client and self._imap_client._client is None:
            # IMAP disconnected, try to reconnect
            try:
                await self._imap_client.connect()
                tracking_duration = self._get_option(
                    CONF_TRACKING_DURATION, DEFAULT_TRACKING_DURATION
                )
                existing = await self._imap_client.fetch_existing_emails(
                    since_days=tracking_duration
                )
                if existing:
                    self._store.merge_packages(existing)
                    await self._store.async_save()
                await self._imap_client.start_idle()
            except Exception as err:
                _LOGGER.warning("Fallback polling - IMAP reconnect failed: %s", err)

        # Clean up old packages periodically
        self._store.cleanup_old_packages(max_age_days=60)

        tracking_duration = self._get_option(
            CONF_TRACKING_DURATION, DEFAULT_TRACKING_DURATION
        )
        show_delivered = self._get_option(
            CONF_SHOW_DELIVERED, DEFAULT_SHOW_DELIVERED
        )
        delivered_duration = self._get_option(
            CONF_DELIVERED_DURATION, DEFAULT_DELIVERED_DURATION
        )

        return self._store.get_active_packages(
            tracking_duration=tracking_duration,
            show_delivered=show_delivered,
            delivered_duration=delivered_duration,
        )
