"""Config flow for Amazon Package Tracker integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import (
    AMAZON_DOMAINS,
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
    DEFAULT_DOMAIN,
    DEFAULT_IMAP_FOLDER,
    DEFAULT_IMAP_PORT,
    DEFAULT_IMAP_SSL,
    DEFAULT_SHOW_DELIVERED,
    DEFAULT_TRACKING_DURATION,
    DOMAIN,
)
from .imap_client import ImapClient

_LOGGER = logging.getLogger(__name__)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Amazon Package Tracker."""

    VERSION = 2

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._imap_data: dict[str, Any] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Step 1: IMAP connection settings."""
        errors = {}

        if user_input is not None:
            # Test IMAP connection
            try:
                success = await ImapClient.test_connection(
                    server=user_input[CONF_IMAP_SERVER],
                    port=user_input[CONF_IMAP_PORT],
                    email_addr=user_input[CONF_IMAP_EMAIL],
                    password=user_input[CONF_IMAP_PASSWORD],
                    ssl=user_input.get(CONF_IMAP_SSL, DEFAULT_IMAP_SSL),
                    folder=user_input.get(CONF_IMAP_FOLDER, DEFAULT_IMAP_FOLDER),
                )
                if success:
                    self._imap_data = user_input
                    return await self.async_step_amazon()
                else:
                    errors["base"] = "invalid_auth"
            except ConnectionError:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected error during IMAP connection test")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_IMAP_SERVER): str,
                    vol.Required(
                        CONF_IMAP_PORT, default=DEFAULT_IMAP_PORT
                    ): int,
                    vol.Required(CONF_IMAP_EMAIL): str,
                    vol.Required(CONF_IMAP_PASSWORD): str,
                    vol.Required(
                        CONF_IMAP_SSL, default=DEFAULT_IMAP_SSL
                    ): bool,
                    vol.Optional(
                        CONF_IMAP_FOLDER, default=DEFAULT_IMAP_FOLDER
                    ): str,
                }
            ),
            errors=errors,
        )

    async def async_step_amazon(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Step 2: Amazon settings."""
        if user_input is not None:
            # Set unique ID based on IMAP email
            await self.async_set_unique_id(self._imap_data[CONF_IMAP_EMAIL])
            self._abort_if_unique_id_configured()

            # Combine IMAP data with Amazon settings
            data = {**self._imap_data}
            options = {
                CONF_AMAZON_DOMAINS: user_input.get(
                    CONF_AMAZON_DOMAINS, [DEFAULT_DOMAIN]
                ),
                CONF_TRACKING_DURATION: user_input.get(
                    CONF_TRACKING_DURATION, DEFAULT_TRACKING_DURATION
                ),
                CONF_SHOW_DELIVERED: user_input.get(
                    CONF_SHOW_DELIVERED, DEFAULT_SHOW_DELIVERED
                ),
                CONF_DELIVERED_DURATION: user_input.get(
                    CONF_DELIVERED_DURATION, DEFAULT_DELIVERED_DURATION
                ),
            }

            return self.async_create_entry(
                title=f"Amazon Tracker ({self._imap_data[CONF_IMAP_EMAIL]})",
                data=data,
                options=options,
            )

        # Build domain options for multi-select
        domain_options = {
            domain: config["name"]
            for domain, config in AMAZON_DOMAINS.items()
        }

        return self.async_show_form(
            step_id="amazon",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_AMAZON_DOMAINS, default=[DEFAULT_DOMAIN]
                    ): vol.All(
                        [vol.In(domain_options)],
                        vol.Length(min=1),
                    ),
                    vol.Required(
                        CONF_TRACKING_DURATION,
                        default=DEFAULT_TRACKING_DURATION,
                    ): vol.All(int, vol.Range(min=1, max=90)),
                    vol.Required(
                        CONF_SHOW_DELIVERED,
                        default=DEFAULT_SHOW_DELIVERED,
                    ): bool,
                    vol.Required(
                        CONF_DELIVERED_DURATION,
                        default=DEFAULT_DELIVERED_DURATION,
                    ): vol.All(int, vol.Range(min=1, max=30)),
                }
            ),
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> OptionsFlowHandler:
        """Get the options flow handler."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Amazon Package Tracker."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self._config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle options flow."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        domain_options = {
            domain: config["name"]
            for domain, config in AMAZON_DOMAINS.items()
        }

        current_domains = self._config_entry.options.get(
            CONF_AMAZON_DOMAINS, [DEFAULT_DOMAIN]
        )
        current_tracking = self._config_entry.options.get(
            CONF_TRACKING_DURATION, DEFAULT_TRACKING_DURATION
        )
        current_show = self._config_entry.options.get(
            CONF_SHOW_DELIVERED, DEFAULT_SHOW_DELIVERED
        )
        current_delivered = self._config_entry.options.get(
            CONF_DELIVERED_DURATION, DEFAULT_DELIVERED_DURATION
        )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_AMAZON_DOMAINS, default=current_domains
                    ): vol.All(
                        [vol.In(domain_options)],
                        vol.Length(min=1),
                    ),
                    vol.Required(
                        CONF_TRACKING_DURATION, default=current_tracking
                    ): vol.All(int, vol.Range(min=1, max=90)),
                    vol.Required(
                        CONF_SHOW_DELIVERED, default=current_show
                    ): bool,
                    vol.Required(
                        CONF_DELIVERED_DURATION, default=current_delivered
                    ): vol.All(int, vol.Range(min=1, max=30)),
                }
            ),
        )
