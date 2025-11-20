
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

SENSORS=["pv_power","load_power","grid_power","battery_power","battery_soc"]

async def async_setup_entry(hass, entry, async_add_entities):
    coord=hass.data[DOMAIN][entry.entry_id]["coordinator"]
    ents=[SolArkSensor(coord, entry, k) for k in SENSORS]
    async_add_entities(ents)

class SolArkSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, entry, key):
        super().__init__(coordinator)
        self._key=key
        self._attr_name=f"SolArk {key.replace('_',' ').title()}"
        self._attr_unique_id=f"{entry.entry_id}_{key}"

    @property
    def native_value(self):
        return self.coordinator.data.get(self._key)
