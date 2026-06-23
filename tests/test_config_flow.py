"""Tests for the Apparent Temperature config flow."""

from __future__ import annotations

from typing import Final

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.apparent_temperature.const import (
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

TEST_TEMP: Final = "sensor.outdoor_temperature"
TEST_HUMIDITY: Final = "sensor.outdoor_humidity"
TEST_WIND: Final = "sensor.wind_speed"
TEST_WEATHER: Final = "weather.outdoor"
TEST_CLIMATE: Final = "climate.living_room"


async def test_user_step_shows_type_form(hass: HomeAssistant) -> None:
    """Test the user step shows setup type selection."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"
    assert not result.get("errors")


async def test_user_step_manual_proceeds_to_manual_config(hass: HomeAssistant) -> None:
    """Test selecting manual type proceeds to the manual_config step."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_SETUP_TYPE: SETUP_TYPE_MANUAL}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "manual_config"


async def test_user_step_weather_proceeds_to_weather_config(hass: HomeAssistant) -> None:
    """Test selecting weather type proceeds to the weather_config step."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_SETUP_TYPE: SETUP_TYPE_WEATHER}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "weather_config"


async def test_user_step_climate_proceeds_to_climate_config(hass: HomeAssistant) -> None:
    """Test selecting climate type proceeds to the climate_config step."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_SETUP_TYPE: SETUP_TYPE_CLIMATE}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "climate_config"


async def test_manual_config_creates_entry(hass: HomeAssistant) -> None:
    """Test that valid manual input creates a config entry."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_SETUP_TYPE: SETUP_TYPE_MANUAL}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_TEMPERATURE: TEST_TEMP, CONF_HUMIDITY: TEST_HUMIDITY},
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "Apparent Temperature"
    assert result["data"][CONF_SETUP_TYPE] == SETUP_TYPE_MANUAL
    assert result["data"][CONF_TEMPERATURE] == TEST_TEMP
    assert result["data"][CONF_HUMIDITY] == TEST_HUMIDITY
    assert not result["data"].get(CONF_NAME)


async def test_manual_config_with_wind_and_name(hass: HomeAssistant) -> None:
    """Test manual config with optional wind speed and custom name."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_SETUP_TYPE: SETUP_TYPE_MANUAL}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_TEMPERATURE: TEST_TEMP,
            CONF_HUMIDITY: TEST_HUMIDITY,
            CONF_WIND_SPEED: TEST_WIND,
            CONF_NAME: "Garden Feels Like",
        },
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "Garden Feels Like"
    assert result["data"][CONF_WIND_SPEED] == TEST_WIND
    assert result["data"][CONF_NAME] == "Garden Feels Like"


async def test_weather_config_creates_entry(hass: HomeAssistant) -> None:
    """Test that weather entity selection creates a config entry."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_SETUP_TYPE: SETUP_TYPE_WEATHER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_WEATHER_ENTITY: TEST_WEATHER}
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "Apparent Temperature"
    assert result["data"][CONF_SETUP_TYPE] == SETUP_TYPE_WEATHER
    assert result["data"][CONF_WEATHER_ENTITY] == TEST_WEATHER


async def test_weather_config_with_name(hass: HomeAssistant) -> None:
    """Test that weather config with a custom name uses it as title."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_SETUP_TYPE: SETUP_TYPE_WEATHER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_WEATHER_ENTITY: TEST_WEATHER, CONF_NAME: "My Feels Like"},
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "My Feels Like"


async def test_climate_config_creates_entry(hass: HomeAssistant) -> None:
    """Test that climate entity selection creates a config entry."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_SETUP_TYPE: SETUP_TYPE_CLIMATE}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_CLIMATE_ENTITY: TEST_CLIMATE, CONF_WIND_SPEED: TEST_WIND},
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"][CONF_SETUP_TYPE] == SETUP_TYPE_CLIMATE
    assert result["data"][CONF_CLIMATE_ENTITY] == TEST_CLIMATE
    assert result["data"][CONF_WIND_SPEED] == TEST_WIND


async def test_options_flow_manual_shows_prefilled_form(hass: HomeAssistant) -> None:
    """Test options flow for manual type shows a pre-filled form."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_SETUP_TYPE: SETUP_TYPE_MANUAL,
            CONF_TEMPERATURE: TEST_TEMP,
            CONF_HUMIDITY: TEST_HUMIDITY,
        },
        title="Apparent Temperature",
    )
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "manual_config"

    schema = result["data_schema"].schema
    temp_key = next(k for k in schema if k == CONF_TEMPERATURE)
    hum_key = next(k for k in schema if k == CONF_HUMIDITY)
    assert temp_key.default() == TEST_TEMP
    assert hum_key.default() == TEST_HUMIDITY


async def test_options_flow_weather_shows_prefilled_form(hass: HomeAssistant) -> None:
    """Test options flow for weather type shows a pre-filled form."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_SETUP_TYPE: SETUP_TYPE_WEATHER, CONF_WEATHER_ENTITY: TEST_WEATHER},
        title="Apparent Temperature",
    )
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "weather_config"

    schema = result["data_schema"].schema
    weather_key = next(k for k in schema if k == CONF_WEATHER_ENTITY)
    assert weather_key.default() == TEST_WEATHER


async def test_options_flow_climate_shows_prefilled_form(hass: HomeAssistant) -> None:
    """Test options flow for climate type shows a pre-filled form."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_SETUP_TYPE: SETUP_TYPE_CLIMATE, CONF_CLIMATE_ENTITY: TEST_CLIMATE},
        title="Apparent Temperature",
    )
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "climate_config"

    schema = result["data_schema"].schema
    climate_key = next(k for k in schema if k == CONF_CLIMATE_ENTITY)
    assert climate_key.default() == TEST_CLIMATE


async def test_options_flow_saves_changes(hass: HomeAssistant) -> None:
    """Test that options changes are stored in entry.options."""
    new_temp = "sensor.indoor_temperature"
    new_hum = "sensor.indoor_humidity"

    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_SETUP_TYPE: SETUP_TYPE_MANUAL,
            CONF_TEMPERATURE: TEST_TEMP,
            CONF_HUMIDITY: TEST_HUMIDITY,
        },
        title="Apparent Temperature",
    )
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {CONF_TEMPERATURE: new_temp, CONF_HUMIDITY: new_hum, CONF_NAME: "Updated"},
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert entry.options[CONF_TEMPERATURE] == new_temp
    assert entry.options[CONF_HUMIDITY] == new_hum
    assert entry.options[CONF_NAME] == "Updated"


async def test_options_flow_reads_from_options_over_data(hass: HomeAssistant) -> None:
    """Test options form pre-fills from entry.options when both data and options exist."""
    overridden_temp = "sensor.override_temperature"

    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_SETUP_TYPE: SETUP_TYPE_MANUAL,
            CONF_TEMPERATURE: TEST_TEMP,
            CONF_HUMIDITY: TEST_HUMIDITY,
        },
        options={
            CONF_SETUP_TYPE: SETUP_TYPE_MANUAL,
            CONF_TEMPERATURE: overridden_temp,
            CONF_HUMIDITY: TEST_HUMIDITY,
        },
        title="Apparent Temperature",
    )
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    result = await hass.config_entries.options.async_init(entry.entry_id)
    schema = result["data_schema"].schema
    temp_key = next(k for k in schema if k == CONF_TEMPERATURE)
    assert temp_key.default() == overridden_temp
