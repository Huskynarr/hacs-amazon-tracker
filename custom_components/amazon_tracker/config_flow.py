"""Config flow for Amazon Package Tracker integration."""
from __future__ import annotations

import logging
from typing import Any
import voluptuous as vol
import aiohttp
from urllib.parse import urlencode

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, CONF_DOMAIN, AMAZON_DOMAINS, DEFAULT_DOMAIN

_LOGGER = logging.getLogger(__name__)

AMAZON_AUTH_URL = "https://www.amazon.de/ap/signin"
AMAZON_REDIRECT_URI = "{base_url}/auth/external/callback"

class AmazonAuthError(HomeAssistantError):
    """Base class for Amazon auth errors."""

class InvalidAuth(AmazonAuthError):
    """Error to indicate there is invalid auth."""

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Amazon Package Tracker."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._email = None
        self._password = None
        self._domain = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            try:
                # Store credentials temporarily
                self._email = user_input["email"]
                self._password = user_input["password"]
                self._domain = user_input.get(CONF_DOMAIN, DEFAULT_DOMAIN)

                # Check if this config entry exists
                await self.async_set_unique_id(f"{self._email}_{self._domain}")
                self._abort_if_unique_id_configured()

                # Create the config entry
                return self.async_create_entry(
                    title=f"Amazon Package Tracker ({self._email} - {AMAZON_DOMAINS[self._domain]['name']})",
                    data={
                        "email": self._email,
                        "password": self._password,
                        CONF_DOMAIN: self._domain,
                    },
                )

            except Exception as err:
                _LOGGER.error("Error during Amazon authentication: %s", err)
                errors["base"] = "unknown"

        # Create domain selector options
        domain_options = {
            domain: config["name"]
            for domain, config in AMAZON_DOMAINS.items()
        }

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("email"): str,
                    vol.Required("password"): str,
                    vol.Required(CONF_DOMAIN, default=DEFAULT_DOMAIN): vol.In(domain_options),
                }
            ),
            errors=errors,
        )

    async def async_step_import(self, import_info: dict[str, Any]) -> FlowResult:
        """Handle import from configuration.yaml."""
        return await self.async_step_user(import_info) 