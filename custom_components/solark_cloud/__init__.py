"""Sol-Ark Cloud Integration for Home Assistant."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_SCAN_INTERVAL, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import (
    CONF_AUTH_MODE,
    CONF_BASE_URL,
    CONF_EMAIL,
    CONF_PLANT_ID,
    DEFAULT_AUTH_MODE,
    DEFAULT_BASE_URL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)
from .solark_api import SolArkAPI, SolArkAPIError, SolArkAuthError, SolArkConnectionError

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Sol-Ark Cloud from a config entry."""
    session = async_get_clientsession(hass)
    
    # Get configuration
    email = entry.data[CONF_EMAIL]
    password = entry.data[CONF_PASSWORD]
    plant_id = entry.data[CONF_PLANT_ID]
    base_url = entry.options.get(
        CONF_BASE_URL, entry.data.get(CONF_BASE_URL, DEFAULT_BASE_URL)
    )
    auth_mode = entry.options.get(
        CONF_AUTH_MODE, entry.data.get(CONF_AUTH_MODE, DEFAULT_AUTH_MODE)
    )
    scan_interval = entry.options.get(
        CONF_SCAN_INTERVAL, entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
    )

    # Create API client
    api = SolArkAPI(
        session=session,
        email=email,
        password=password,
        base_url=base_url,
        auth_mode=auth_mode,
    )

    # Authenticate
    try:
        auth_success = await api.authenticate()
        if not auth_success:
            raise ConfigEntryAuthFailed("Authentication failed")
    except SolArkAuthError as err:
        raise ConfigEntryAuthFailed(f"Authentication failed: {err}") from err
    except SolArkConnectionError as err:
        raise ConfigEntryNotReady(f"Cannot connect to Sol-Ark Cloud: {err}") from err
    except Exception as err:
        _LOGGER.exception("Unexpected error during setup: %s", err)
        raise ConfigEntryNotReady(f"Setup failed: {err}") from err

    # Create coordinator
    coordinator = SolArkDataUpdateCoordinator(
        hass,
        api=api,
        plant_id=plant_id,
        update_interval=timedelta(seconds=scan_interval),
    )

    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()

    # Store coordinator
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Setup platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Setup options update listener
    entry.async_on_unload(entry.add_update_listener(async_update_options))

    return True


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        coordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.api.close()

    return unload_ok


class SolArkDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Sol-Ark data."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: SolArkAPI,
        plant_id: str,
        update_interval: timedelta,
    ) -> None:
        """Initialize."""
        self.api = api
        self.plant_id = plant_id

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=update_interval,
        )

    async def _async_update_data(self):
        """Fetch data from API."""
        try:
            data = await self.api.get_plant_data(self.plant_id)
            if not data:
                raise UpdateFailed("No data received from Sol-Ark API")
            return data
        except SolArkAuthError as err:
            # Token expired, try to re-authenticate
            try:
                await self.api.authenticate()
                data = await self.api.get_plant_data(self.plant_id)
                if not data:
                    raise UpdateFailed("No data received after re-authentication")
                return data
            except SolArkAuthError as auth_err:
                raise ConfigEntryAuthFailed(
                    f"Re-authentication failed: {auth_err}"
                ) from auth_err
        except SolArkConnectionError as err:
            raise UpdateFailed(f"Connection error: {err}") from err
        except SolArkAPIError as err:
            raise UpdateFailed(f"API error: {err}") from err
        except Exception as err:
            _LOGGER.exception("Unexpected error fetching data: %s", err)
            raise UpdateFailed(f"Unexpected error: {err}") from err
