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

from .const import DOMAIN

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

                # Generate Amazon login URL
                hass_url = self.hass.config.external_url
                if not hass_url:
                    hass_url = self.hass.config.internal_url
                
                redirect_uri = AMAZON_REDIRECT_URI.format(base_url=hass_url)
                
                # Amazon OAuth parameters
                params = {
                    "openid.pape.max_auth_age": "0",
                    "openid.return_to": f"{hass_url}/auth/external/callback",
                    "openid.identity": "http://specs.openid.net/auth/2.0/identifier_select",
                    "openid.assoc_handle": "deflex",
                    "openid.mode": "checkid_setup",
                    "openid.claimed_id": "http://specs.openid.net/auth/2.0/identifier_select",
                    "openid.ns": "http://specs.openid.net/auth/2.0",
                    "client_id": "amzn1.application-oa2-client.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",  # Replace with your client ID
                    "response_type": "code",
                    "scope": "profile",
                    "redirect_uri": redirect_uri
                }

                # Redirect to Amazon login
                return self.async_external_step(
                    step_id="amazon_auth",
                    url=f"{AMAZON_AUTH_URL}?{urlencode(params)}",
                    description_placeholders={
                        "url": AMAZON_AUTH_URL,
                    },
                )

            except Exception as err:
                _LOGGER.error("Error during Amazon authentication: %s", err)
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("email"): str,
                    vol.Required("password"): str,
                }
            ),
            errors=errors,
        )

    async def async_step_amazon_auth(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the Amazon OAuth callback."""
        if not user_input:
            return self.async_abort(reason="no_code")

        try:
            # Verify the authentication
            session = async_get_clientsession(self.hass)
            async with session.post(
                "https://api.amazon.com/auth/o2/token",
                data={
                    "grant_type": "authorization_code",
                    "code": user_input["code"],
                    "client_id": "amzn1.application-oa2-client.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",  # Replace with your client ID
                    "client_secret": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",  # Replace with your client secret
                    "redirect_uri": AMAZON_REDIRECT_URI.format(
                        base_url=self.hass.config.external_url or self.hass.config.internal_url
                    ),
                },
            ) as response:
                if response.status != 200:
                    raise InvalidAuth

                # Create the config entry
                return self.async_create_entry(
                    title=f"Amazon Package Tracker ({self._email})",
                    data={
                        "email": self._email,
                        "password": self._password,
                    },
                )

        except InvalidAuth:
            return self.async_abort(reason="invalid_auth")
        except Exception as err:
            _LOGGER.error("Error during Amazon OAuth callback: %s", err)
            return self.async_abort(reason="unknown")

    async def async_step_import(self, import_info: dict[str, Any]) -> FlowResult:
        """Handle import from configuration.yaml."""
        return await self.async_step_user(import_info) 