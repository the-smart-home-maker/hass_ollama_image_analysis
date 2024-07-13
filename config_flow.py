"""Config flow for Ollama (local AI models) image analysis integration."""

from __future__ import annotations

import logging
from typing import Any
import re

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant, HomeAssistantError

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema({vol.Required(CONF_HOST): str})


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """

    # If your PyPI package is not built with async, pass your methods
    # to the executor:
    # await hass.async_add_executor_job(
    #     your_validate_func, data[CONF_USERNAME], data[CONF_PASSWORD]
    # )

    p = "(?:http.*://)(?P<host>[^:/ ]+).?(?P<port>[0-9]*).*"

    result = re.match(p, data[CONF_HOST])

    if not result:
        raise InvalidUrlScheme

    # Return info that you want to store in the config entry.
    return {"host": data[CONF_HOST]}


class ConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Ollama (local AI models) image analysis."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                await validate_input(self.hass, user_input)
            except InvalidUrlScheme:
                errors["base"] = "invalid_url_scheme"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title="Ollama (local AI models) image analysis", data=user_input
                )

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class InvalidUrlScheme(HomeAssistantError):
    """Error to indicate we cannot connect."""
