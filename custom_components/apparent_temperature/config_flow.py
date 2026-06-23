"""Config flow for Apparent Temperature."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.const import CONF_NAME
from homeassistant.core import callback
from homeassistant.helpers import area_registry as ar
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
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
    CONF_DISCOVER_BY,
    CONF_DISCOVER_SELECTION,
    CONF_HUMIDITY,
    CONF_SETUP_TYPE,
    CONF_TEMPERATURE,
    CONF_WEATHER_ENTITY,
    CONF_WIND_SPEED,
    DISCOVER_BY_AREA,
    DISCOVER_BY_DEVICE,
    DOMAIN,
    SETUP_TYPE_CLIMATE,
    SETUP_TYPE_DISCOVER,
    SETUP_TYPE_MANUAL,
    SETUP_TYPE_WEATHER,
)

STEP_DISCOVER_BY_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_DISCOVER_BY): SelectSelector(
            SelectSelectorConfig(
                options=[
                    {"value": DISCOVER_BY_AREA, "label": "By room (HA area)"},
                    {"value": DISCOVER_BY_DEVICE, "label": "By device"},
                    {"value": "back", "label": "← Change setup type"},
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


def _discover_select_schema(pairs: list[dict]) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(CONF_DISCOVER_SELECTION): SelectSelector(
                SelectSelectorConfig(
                    options=[
                        {"value": p[CONF_TEMPERATURE], "label": p["label"]}
                        for p in pairs
                    ],
                    multiple=True,
                    mode=SelectSelectorMode.LIST,
                )
            )
        }
    )


class ApparentTemperatureConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Apparent Temperature."""

    VERSION = 1
    MINOR_VERSION = 1

    def __init__(self) -> None:
        """Initialise flow instance state."""
        self._discovered_pairs: list[dict] = []

    # ------------------------------------------------------------------
    # Step 1: type selection (menu)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Show the setup-type menu."""
        return self.async_show_menu(
            step_id="user",
            menu_options=["manual_config", "weather_config", "climate_config", "discover"],
        )

    # ------------------------------------------------------------------
    # Manual / Weather / Climate config steps

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

    # ------------------------------------------------------------------
    # Auto-discover steps

    async def async_step_discover(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Entry point from the user menu — go straight to grouping choice."""
        return await self.async_step_discover_by()

    async def async_step_discover_by(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Ask whether to group by area or by device."""
        errors: dict[str, str] = {}

        if user_input is not None:
            discover_by = user_input[CONF_DISCOVER_BY]
            if discover_by == "back":
                return await self.async_step_user()
            pairs = (
                self._find_area_pairs()
                if discover_by == DISCOVER_BY_AREA
                else self._find_device_pairs()
            )
            if pairs:
                self._discovered_pairs = pairs
                return await self.async_step_discover_select()
            errors[CONF_DISCOVER_BY] = "no_devices_found"

        return self.async_show_form(
            step_id="discover_by",
            data_schema=STEP_DISCOVER_BY_SCHEMA,
            errors=errors,
        )

    async def async_step_discover_select(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Show the list of discovered candidates and let the user pick."""
        pairs = self._discovered_pairs

        if user_input is not None:
            selected_temps: list[str] = user_input[CONF_DISCOVER_SELECTION]
            selected = [p for p in pairs if p[CONF_TEMPERATURE] in selected_temps]

            # Enqueue additional entries as import flows so they are created
            # without requiring the user to step through the UI again.
            for pair in selected[1:]:
                self.hass.async_create_task(
                    self.hass.config_entries.flow.async_init(
                        DOMAIN,
                        context={"source": config_entries.SOURCE_IMPORT},
                        data={
                            CONF_SETUP_TYPE: SETUP_TYPE_MANUAL,
                            CONF_TEMPERATURE: pair[CONF_TEMPERATURE],
                            CONF_HUMIDITY: pair[CONF_HUMIDITY],
                            CONF_NAME: pair["label"],
                        },
                    )
                )

            first = selected[0]
            return self.async_create_entry(
                title=first["label"],
                data={
                    CONF_SETUP_TYPE: SETUP_TYPE_MANUAL,
                    CONF_TEMPERATURE: first[CONF_TEMPERATURE],
                    CONF_HUMIDITY: first[CONF_HUMIDITY],
                    CONF_NAME: first["label"],
                },
            )

        return self.async_show_form(
            step_id="discover_select",
            data_schema=_discover_select_schema(pairs),
        )

    async def async_step_import(
        self, import_data: dict[str, Any]
    ) -> config_entries.ConfigFlowResult:
        """Create an entry from auto-discovery without showing a form."""
        return self.async_create_entry(
            title=import_data.get(CONF_NAME, "Apparent Temperature"),
            data=import_data,
        )

    # ------------------------------------------------------------------
    # Discovery helpers

    def _configured_temperature_entities(self) -> set[str]:
        """Return temperature entity IDs already used by existing entries."""
        result: set[str] = set()
        for entry in self.hass.config_entries.async_entries(DOMAIN):
            data = {**entry.data, **entry.options}
            if temp := data.get(CONF_TEMPERATURE):
                result.add(temp)
        return result

    def _find_area_pairs(self) -> list[dict]:
        """Find temp+humidity sensor pairs grouped by HA area."""
        area_reg = ar.async_get(self.hass)
        device_reg = dr.async_get(self.hass)
        entity_reg = er.async_get(self.hass)
        already_used = self._configured_temperature_entities()

        area_temps: dict[str, str] = {}
        area_humids: dict[str, str] = {}

        for entity in entity_reg.entities.values():
            if entity.domain != "sensor" or entity.platform == DOMAIN:
                continue

            # Resolve area: prefer entity-level, fall back to device-level
            area_id = entity.area_id
            if area_id is None and entity.device_id:
                device = device_reg.async_get(entity.device_id)
                if device:
                    area_id = device.area_id
            if area_id is None:
                continue

            device_class = entity.device_class or entity.original_device_class
            if device_class == SensorDeviceClass.TEMPERATURE:
                area_temps.setdefault(area_id, entity.entity_id)
            elif device_class == SensorDeviceClass.HUMIDITY:
                area_humids.setdefault(area_id, entity.entity_id)

        pairs = []
        for area_id, temp_id in area_temps.items():
            if area_id not in area_humids or temp_id in already_used:
                continue
            area = area_reg.async_get_area(area_id)
            if area is None:
                continue
            pairs.append(
                {
                    "label": area.name,
                    CONF_TEMPERATURE: temp_id,
                    CONF_HUMIDITY: area_humids[area_id],
                }
            )

        pairs.sort(key=lambda p: p["label"])
        return pairs

    def _find_device_pairs(self) -> list[dict]:
        """Find temp+humidity sensor pairs grouped by device."""
        device_reg = dr.async_get(self.hass)
        entity_reg = er.async_get(self.hass)
        already_used = self._configured_temperature_entities()

        device_temps: dict[str, str] = {}
        device_humids: dict[str, str] = {}

        for entity in entity_reg.entities.values():
            if entity.domain != "sensor" or entity.platform == DOMAIN or not entity.device_id:
                continue
            device_class = entity.device_class or entity.original_device_class
            if device_class == SensorDeviceClass.TEMPERATURE:
                device_temps.setdefault(entity.device_id, entity.entity_id)
            elif device_class == SensorDeviceClass.HUMIDITY:
                device_humids.setdefault(entity.device_id, entity.entity_id)

        pairs = []
        for device_id, temp_id in device_temps.items():
            if device_id not in device_humids or temp_id in already_used:
                continue
            device = device_reg.async_get(device_id)
            if device is None:
                continue
            label = device.name_by_user or device.name or device_id
            pairs.append(
                {
                    "label": label,
                    CONF_TEMPERATURE: temp_id,
                    CONF_HUMIDITY: device_humids[device_id],
                }
            )

        pairs.sort(key=lambda p: p["label"])
        return pairs

    # ------------------------------------------------------------------

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
        # SETUP_TYPE_MANUAL and SETUP_TYPE_DISCOVER both edit via manual_config
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
