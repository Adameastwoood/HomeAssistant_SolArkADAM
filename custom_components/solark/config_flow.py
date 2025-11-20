"""Config flow for SolArk."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    DOMAIN,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_PLANT_ID,
    CONF_BASE_URL,
    CONF_API_URL,
    DEFAULT_BASE_URL,
    DEFAULT_API_URL,
)
from .api import SolArkCloudAPI, SolArkCloudAPIError

_LOGGER = logging.getLogger(__name__)


async def _test_connection(
    hass: HomeAssistant, data: dict[str, Any]
) -> tuple[bool, str | None]:
    session = async_get_clientsession(hass)
    api = SolArkCloudAPI(
        username=data[CONF_USERNAME],
        password=data[CONF_PASSWORD],
        plant_id=data[CONF_PLANT_ID],
        base_url=data.get(CONF_BASE_URL, DEFAULT_BASE_URL),
        api_url=data.get(CONF_API_URL, DEFAULT_API_URL),
        session=session,
    )

    try:
        ok = await api.test_connection()
        if ok:
            return True, None
        return False, "cannot_connect"
    except SolArkCloudAPIError as e:  # noqa: BLE001
        _LOGGER.error("SolArk test_connection failed: %s", e)
        return False, "auth_failed"
    except Exception as e:  # noqa: BLE001
        _LOGGER.exception("Unexpected exception testing SolArk connection: %s", e)
        return False, "unknown"


class SolArkConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for SolArk."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            ok, reason = await _test_connection(self.hass, user_input)
            if ok:
                unique_id = f"{user_input[CONF_USERNAME]}_{user_input[CONF_PLANT_ID]}"
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"SolArk {user_input[CONF_PLANT_ID]}",
                    data={
                        CONF_USERNAME: user_input[CONF_USERNAME],
                        CONF_PASSWORD: user_input[CONF_PASSWORD],
                        CONF_PLANT_ID: user_input[CONF_PLANT_ID],
                        CONF_BASE_URL: user_input.get(CONF_BASE_URL, DEFAULT_BASE_URL),
                        CONF_API_URL: user_input.get(CONF_API_URL, DEFAULT_API_URL),
                    },
                )

            errors["base"] = reason or "unknown"

        data_schema = vol.Schema(
            {
                vol.Required(CONF_USERNAME): str,
                vol.Required(CONF_PASSWORD): str,
                vol.Required(CONF_PLANT_ID): str,
                vol.Optional(CONF_BASE_URL, default=DEFAULT_BASE_URL): str,
                vol.Optional(CONF_API_URL, default=DEFAULT_API_URL): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )
