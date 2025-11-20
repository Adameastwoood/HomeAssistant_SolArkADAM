
import logging
from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .const import DOMAIN, CONF_USERNAME, CONF_PASSWORD, CONF_PLANT_ID, CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL, PLATFORMS
from .api import SolArkCloudAPI

_LOGGER=logging.getLogger(__name__)

async def async_setup(hass, config): return True

async def async_setup_entry(hass:HomeAssistant, entry:ConfigEntry):
    hass.data.setdefault(DOMAIN,{})
    session=async_get_clientsession(hass)
    api=SolArkCloudAPI(session, entry.data[CONF_USERNAME], entry.data[CONF_PASSWORD], entry.data[CONF_PLANT_ID])

    async def update():
        raw=await api.get_plant_data()
        return api.compute_values(raw)

    coord=DataUpdateCoordinator(hass,_LOGGER,name="solark",update_method=update,update_interval=timedelta(seconds=entry.data.get(CONF_SCAN_INTERVAL,DEFAULT_SCAN_INTERVAL)))
    await coord.async_config_entry_first_refresh()
    hass.data[DOMAIN][entry.entry_id]={"coordinator":coord}
    await hass.config_entries.async_forward_entry_setups(entry,PLATFORMS)
    return True
