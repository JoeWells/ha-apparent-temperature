"""Constants for apparent_temperature."""

# Base component constants
from typing import Final

NAME: Final = "Apparent Temperature"
DOMAIN: Final = "apparent_temperature"
VERSION: Final = "1.1.1"
ISSUE_URL: Final = "https://github.com/Limych/ha-temperature-feeling/issues"

STARTUP_MESSAGE: Final = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
This is a custom integration!
If you have ANY issues with this you need to open an issue here:
{ISSUE_URL}
-------------------------------------------------------------------
"""


# Config flow keys
CONF_TEMPERATURE: Final = "temperature"
CONF_HUMIDITY: Final = "humidity"
CONF_WIND_SPEED: Final = "wind_speed"
CONF_WEATHER_ENTITY: Final = "weather"
CONF_CLIMATE_ENTITY: Final = "climate"
CONF_SETUP_TYPE: Final = "setup_type"

SETUP_TYPE_MANUAL: Final = "manual"
SETUP_TYPE_WEATHER: Final = "weather"
SETUP_TYPE_CLIMATE: Final = "climate"


# Attributes
ATTR_TEMPERATURE_SOURCE: Final = "temperature_source"
ATTR_TEMPERATURE_SOURCE_VALUE: Final = "temperature_source_value"
ATTR_HUMIDITY_SOURCE: Final = "humidity_source"
ATTR_HUMIDITY_SOURCE_VALUE: Final = "humidity_source_value"
ATTR_WIND_SPEED_SOURCE: Final = "wind_speed_source"
ATTR_WIND_SPEED_SOURCE_VALUE: Final = "wind_speed_source_value"
