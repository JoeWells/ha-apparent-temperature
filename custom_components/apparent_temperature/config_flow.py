"""Config flow for Apparent Temperature."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import callback
from homeassistant.helpers.selector import (
    EntitySelector,
    EntitySelectorConfig,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .const import (
    CONF_CLIMATE_ENTITY,
    CONF_HUMIDITY,
    CONF_SETUP_TYPE,
    CONF_TEMPERATURE,
    CONF_WEATHER_ENTITY,
    CONF_WIND_SPEED,
    DOMAIN,
    SETUP_TYPE_CLIMATE,
    SETUP_TYPE_MANUAL,
    SETUP_TYPE_WEATHER,
)

STEP_TYPE_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_SETUP_TYPE): SelectSelector(
            SelectSelectorConfig(
                options=[
                    {"value": SETUP_TYPE_MANUAL, "label": "Manual sensors"},
                    {"value": SETUP_TYPE_WEATHER, "label": "Weather entity"},
                    {"value": SETUP_TYPE_CLIMATE, "label": "Climate entity"},
                ],
                mode=SelectSelectorMode.LIST,
            )
        )
    }
)


def _manual_schema(
    temperature: str = "",
    humidity: str = "",
    wind_speed: str = "",
    name: str = "",
) -> vol.Schema:
    wind_speed_key = (
        vol.Optional(CONF_WIND_SPEED, default=wind_speed)
        if wind_speed
        else vol.Optional(CONF_WIND_SPEED)
    )
    return vol.Schema(
        {
            vol.Required(CONF_TEMPERATURE, default=temperature): EntitySelector(
                EntitySelectorConfig(domain="sensor", device_class="temperature")
            ),
            vol.Required(CONF_HUMIDITY, default=humidity): EntitySelector(
                EntitySelectorConfig(domain="sensor", device_class="humidity")
            ),
            wind_speed_key: EntitySelector(
                EntitySelectorConfig(domain="sensor", device_class="wind_speed")
            ),
            vol.Optional(CONF_NAME, default=name): TextSelector(
                TextSelectorConfig(type=TextSelectorType.TEXT)
            ),
        }
    )


def _weather_schema(weather: str = "", name: str = "") -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(CONF_WEATHER_ENTITY, default=weather): EntitySelector(
                EntitySelectorConfig(domain="weather")
            ),
            vol.Optional(CONF_NAME, default=name): TextSelector(
                TextSelectorConfig(type=TextSelectorType.TEXT)
            ),
        }
    )


def _climate_schema(
    climate: str = "", wind_speed: str = "", name: str = ""
) -> vol.Schema:
    wind_speed_key = (
        vol.Optional(CONF_WIND_SPEED, default=wind_speed)
        if wind_speed
        else vol.Optional(CONF_WIND_SPEED)
    )
    return vol.Schema(
        {
            vol.Required(CONF_CLIMATE_ENTITY, default=climate): EntitySelector(
                EntitySelectorConfig(domain="climate")
            ),
            wind_speed_key: EntitySelector(
                EntitySelectorConfig(domain="sensor", device_class="wind_speed")
            ),
            vol.Optional(CONF_NAME, default=name): TextSelector(
                TextSelectorConfig(type=TextSelectorType.TEXT)
            ),
        }
    )


class ApparentTemperatureConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Apparent Temperature."""

    VERSION = 1
    MINOR_VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle setup type selection."""
        if user_input is not None:
            setup_type = user_input[CONF_SETUP_TYPE]
            if setup_type == SETUP_TYPE_WEATHER:
                return await self.async_step_weather_config()
            if setup_type == SETUP_TYPE_CLIMATE:
                return await self.async_step_climate_config()
            return await self.async_step_manual_config()

        return self.async_show_form(step_id="user", data_schema=STEP_TYPE_SCHEMA)

    async def async_step_manual_config(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle manual sensor selection."""
        if user_input is not None:
            return self.async_create_entry(
                title=user_input.get(CONF_NAME) or "Apparent Temperature",
                data={CONF_SETUP_TYPE: SETUP_TYPE_MANUAL, **user_input},
            )
        return self.async_show_form(
            step_id="manual_config",
            data_schema=_manual_schema(),
        )

    async def async_step_weather_config(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle weather entity selection."""
        if user_input is not None:
            return self.async_create_entry(
                title=user_input.get(CONF_NAME) or "Apparent Temperature",
                data={CONF_SETUP_TYPE: SETUP_TYPE_WEATHER, **user_input},
            )
        return self.async_show_form(
            step_id="weather_config",
            data_schema=_weather_schema(),
        )

    async def async_step_climate_config(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle climate entity selection."""
        if user_input is not None:
            return self.async_create_entry(
                title=user_input.get(CONF_NAME) or "Apparent Temperature",
                data={CONF_SETUP_TYPE: SETUP_TYPE_CLIMATE, **user_input},
            )
        return self.async_show_form(
            step_id="climate_config",
            data_schema=_climate_schema(),
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> ApparentTemperatureOptionsFlow:
        """Return the options flow."""
        return ApparentTemperatureOptionsFlow()


class ApparentTemperatureOptionsFlow(config_entries.OptionsFlow):
    """Options flow for Apparent Temperature."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Route to the appropriate config step based on setup type."""
        data = {**self.config_entry.data, **self.config_entry.options}
        setup_type = data.get(CONF_SETUP_TYPE, SETUP_TYPE_MANUAL)

        if setup_type == SETUP_TYPE_WEATHER:
            return await self.async_step_weather_config()
        if setup_type == SETUP_TYPE_CLIMATE:
            return await self.async_step_climate_config()
        return await self.async_step_manual_config()

    async def async_step_manual_config(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle manual sensor options."""
        if user_input is not None:
            return self.async_create_entry(
                data={CONF_SETUP_TYPE: SETUP_TYPE_MANUAL, **user_input}
            )
        data = {**self.config_entry.data, **self.config_entry.options}
        return self.async_show_form(
            step_id="manual_config",
            data_schema=_manual_schema(
                temperature=data.get(CONF_TEMPERATURE, ""),
                humidity=data.get(CONF_HUMIDITY, ""),
                wind_speed=data.get(CONF_WIND_SPEED, ""),
                name=data.get(CONF_NAME, ""),
            ),
        )

    async def async_step_weather_config(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle weather entity options."""
        if user_input is not None:
            return self.async_create_entry(
                data={CONF_SETUP_TYPE: SETUP_TYPE_WEATHER, **user_input}
            )
        data = {**self.config_entry.data, **self.config_entry.options}
        return self.async_show_form(
            step_id="weather_config",
            data_schema=_weather_schema(
                weather=data.get(CONF_WEATHER_ENTITY, ""),
                name=data.get(CONF_NAME, ""),
            ),
        )

    async def async_step_climate_config(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle climate entity options."""
        if user_input is not None:
            return self.async_create_entry(
                data={CONF_SETUP_TYPE: SETUP_TYPE_CLIMATE, **user_input}
            )
        data = {**self.config_entry.data, **self.config_entry.options}
        return self.async_show_form(
            step_id="climate_config",
            data_schema=_climate_schema(
                climate=data.get(CONF_CLIMATE_ENTITY, ""),
                wind_speed=data.get(CONF_WIND_SPEED, ""),
                name=data.get(CONF_NAME, ""),
            ),
        )
