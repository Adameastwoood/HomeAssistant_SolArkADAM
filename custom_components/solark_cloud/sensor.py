"""Support for Sol-Ark Cloud sensors."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfEnergy,
    UnitOfPower,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import SolArkDataUpdateCoordinator
from .const import DOMAIN, CONF_PLANT_ID


@dataclass
class SolArkSensorEntityDescription(SensorEntityDescription):
    """Describes Sol-Ark sensor entity."""

    value_fn: Callable[[dict[str, Any]], Any] | None = None
    attribute_fn: Callable[[dict[str, Any]], dict[str, Any]] | None = None


SENSOR_TYPES: tuple[SolArkSensorEntityDescription, ...] = (
    SolArkSensorEntityDescription(
        key="pv_power",
        name="PV Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("pac", 0),
    ),
    SolArkSensorEntityDescription(
        key="load_power",
        name="Load Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("familyLoadPower", 0),
    ),
    SolArkSensorEntityDescription(
        key="grid_import_power",
        name="Grid Import Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: max(0, data.get("gridPower", 0)),
    ),
    SolArkSensorEntityDescription(
        key="grid_export_power",
        name="Grid Export Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: abs(min(0, data.get("gridPower", 0))),
    ),
    SolArkSensorEntityDescription(
        key="battery_power",
        name="Battery Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("batPower", 0),
        attribute_fn=lambda data: {
            "status": (
                "charging" if data.get("batPower", 0) < 0
                else "discharging" if data.get("batPower", 0) > 0
                else "idle"
            )
        },
    ),
    SolArkSensorEntityDescription(
        key="battery_state_of_charge",
        name="Battery State of Charge",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("soc", 0),
    ),
    SolArkSensorEntityDescription(
        key="energy_today",
        name="Energy Today",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: data.get("eToday", 0),
    ),
    SolArkSensorEntityDescription(
        key="last_error",
        name="Last Error",
        value_fn=lambda data: data.get("lastError", "None"),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Sol-Ark sensors based on a config entry."""
    coordinator: SolArkDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    plant_id = entry.data[CONF_PLANT_ID]

    entities = [
        SolArkSensor(coordinator, description, plant_id)
        for description in SENSOR_TYPES
    ]

    async_add_entities(entities)


class SolArkSensor(CoordinatorEntity[SolArkDataUpdateCoordinator], SensorEntity):
    """Representation of a Sol-Ark sensor."""

    entity_description: SolArkSensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: SolArkDataUpdateCoordinator,
        description: SolArkSensorEntityDescription,
        plant_id: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{plant_id}_{description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, plant_id)},
            "name": f"Sol-Ark Plant {plant_id}",
            "manufacturer": "Sol-Ark",
            "model": "Cloud Integration",
        }

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        if self.coordinator.data and self.entity_description.value_fn:
            return self.entity_description.value_fn(self.coordinator.data)
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return additional attributes."""
        if self.coordinator.data and self.entity_description.attribute_fn:
            return self.entity_description.attribute_fn(self.coordinator.data)
        return None
