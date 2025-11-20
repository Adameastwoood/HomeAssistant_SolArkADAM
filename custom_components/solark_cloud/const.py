"""Constants for the Sol-Ark Cloud integration."""
from typing import Final

DOMAIN: Final = "solark_cloud"

# Configuration keys
CONF_EMAIL: Final = "email"
CONF_PLANT_ID: Final = "plant_id"
CONF_BASE_URL: Final = "base_url"
CONF_AUTH_MODE: Final = "auth_mode"

# Defaults
DEFAULT_BASE_URL: Final = "https://api.solarkcloud.com"
DEFAULT_AUTH_MODE: Final = "Auto"
DEFAULT_SCAN_INTERVAL: Final = 120

# API Endpoints
LOGIN_ENDPOINT: Final = "/rest/account/login"
PLANT_DATA_ENDPOINT: Final = "/rest/plant/getPlantData"

# Sensor keys
SENSOR_PV_POWER: Final = "pv_power"
SENSOR_LOAD_POWER: Final = "load_power"
SENSOR_GRID_IMPORT: Final = "grid_import_power"
SENSOR_GRID_EXPORT: Final = "grid_export_power"
SENSOR_BATTERY_POWER: Final = "battery_power"
SENSOR_BATTERY_SOC: Final = "battery_state_of_charge"
SENSOR_ENERGY_TODAY: Final = "energy_today"
SENSOR_LAST_ERROR: Final = "last_error"
