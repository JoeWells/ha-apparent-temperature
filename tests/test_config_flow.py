"""Tests for the Apparent Temperature config flow."""

from __future__ import annotations

from typing import Final

from homeassistant import config_entries
from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers import area_registry as ar
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.apparent_temperature.const import (
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

TEST_TEMP: Final = "sensor.outdoor_temperature"
TEST_HUMIDITY: Final = "sensor.outdoor_humidity"
TEST_WIND: Final = "sensor.wind_speed"
TEST_WEATHER: Final = "weather.outdoor"
TEST_CLIMATE: Final = "climate.living_room"


async def _start_flow(hass: HomeAssistant) -> dict:
    """Start a fresh config flow and return the initial (menu) result."""
    return await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )


async def test_user_step_shows_menu(hass: HomeAssistant) -> None:
    """Test the user step shows a setup-type menu (not a form)."""
    result = await _start_flow(hass)
    assert result["type"] is FlowResultType.MENU
    assert result["step_id"] == "user"


async def test_user_step_manual_proceeds_to_manual_config(hass: HomeAssistant) -> None:
    """Test selecting manual proceeds to the manual_config step."""
    result = await _start_flow(hass)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"next_step_id": "manual_config"}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "manual_config"


async def test_user_step_weather_proceeds_to_weather_config(hass: HomeAssistant) -> None:
    """Test selecting weather proceeds to the weather_config step."""
    result = await _start_flow(hass)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"next_step_id": "weather_config"}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "weather_config"


async def test_user_step_climate_proceeds_to_climate_config(hass: HomeAssistant) -> None:
    """Test selecting climate proceeds to the climate_config step."""
    result = await _start_flow(hass)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"next_step_id": "climate_config"}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "climate_config"


async def test_manual_config_creates_entry(hass: HomeAssistant) -> None:
    """Test that valid manual input creates a config entry."""
    result = await _start_flow(hass)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"next_step_id": "manual_config"}
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
    result = await _start_flow(hass)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"next_step_id": "manual_config"}
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
    result = await _start_flow(hass)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"next_step_id": "weather_config"}
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
    result = await _start_flow(hass)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"next_step_id": "weather_config"}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_WEATHER_ENTITY: TEST_WEATHER, CONF_NAME: "My Feels Like"},
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "My Feels Like"


async def test_climate_config_creates_entry(hass: HomeAssistant) -> None:
    """Test that climate entity selection creates a config entry."""
    result = await _start_flow(hass)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"next_step_id": "climate_config"}
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


# ---------------------------------------------------------------------------
# Auto-discover tests
# ---------------------------------------------------------------------------


def _register_sensor(
    entity_reg: er.EntityRegistry,
    platform: str,
    unique_id: str,
    device_class: SensorDeviceClass,
    area_id: str | None = None,
    device_id: str | None = None,
) -> er.RegistryEntry:
    """Helper: create a sensor entity in the registry with a given device class."""
    entry = entity_reg.async_get_or_create(
        "sensor",
        platform,
        unique_id,
        original_device_class=device_class,
        device_id=device_id,
    )
    entity_reg.async_update_entity(entry.entity_id, area_id=area_id)
    return entry


async def test_discover_step_shows_discover_by_form(hass: HomeAssistant) -> None:
    """Selecting auto-discover opens the group-by step."""
    result = await _start_flow(hass)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"next_step_id": "discover"}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "discover_by"


async def test_discover_by_area_shows_error_when_no_pairs(hass: HomeAssistant) -> None:
    """Show an inline error on discover_by when no areas have matching pairs."""
    result = await _start_flow(hass)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"next_step_id": "discover"}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_DISCOVER_BY: DISCOVER_BY_AREA}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "discover_by"
    assert result["errors"] == {CONF_DISCOVER_BY: "no_devices_found"}


async def test_discover_by_back_returns_to_user_menu(hass: HomeAssistant) -> None:
    """Selecting 'back' on the discover_by step returns to the user menu."""
    result = await _start_flow(hass)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"next_step_id": "discover"}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_DISCOVER_BY: "back"}
    )
    assert result["type"] is FlowResultType.MENU
    assert result["step_id"] == "user"


async def test_discover_by_area_shows_select_form(hass: HomeAssistant) -> None:
    """A full area with temp+humidity reaches the discover_select step."""
    area_reg = ar.async_get(hass)
    entity_reg = er.async_get(hass)

    living_room = area_reg.async_create("Living Room")
    _register_sensor(entity_reg, "test", "lr_temp", SensorDeviceClass.TEMPERATURE, area_id=living_room.id)
    _register_sensor(entity_reg, "test", "lr_hum", SensorDeviceClass.HUMIDITY, area_id=living_room.id)

    result = await _start_flow(hass)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"next_step_id": "discover"}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_DISCOVER_BY: DISCOVER_BY_AREA}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "discover_select"


async def test_discover_by_area_creates_entry(hass: HomeAssistant) -> None:
    """Selecting an area pair creates a config entry with the area name as title."""
    area_reg = ar.async_get(hass)
    entity_reg = er.async_get(hass)

    living_room = area_reg.async_create("Living Room")
    temp = _register_sensor(entity_reg, "test", "lr_temp", SensorDeviceClass.TEMPERATURE, area_id=living_room.id)
    hum = _register_sensor(entity_reg, "test", "lr_hum", SensorDeviceClass.HUMIDITY, area_id=living_room.id)

    result = await _start_flow(hass)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"next_step_id": "discover"}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_DISCOVER_BY: DISCOVER_BY_AREA}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_DISCOVER_SELECTION: [temp.entity_id]}
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "Living Room"
    assert result["data"][CONF_TEMPERATURE] == temp.entity_id
    assert result["data"][CONF_HUMIDITY] == hum.entity_id
    assert result["data"][CONF_SETUP_TYPE] == SETUP_TYPE_MANUAL


async def test_discover_multiple_areas_creates_additional_flows(hass: HomeAssistant) -> None:
    """Selecting multiple areas creates one entry plus queued flows for the rest."""
    area_reg = ar.async_get(hass)
    entity_reg = er.async_get(hass)

    kitchen = area_reg.async_create("Kitchen")
    bedroom = area_reg.async_create("Bedroom")

    kt = _register_sensor(entity_reg, "test", "kt_temp", SensorDeviceClass.TEMPERATURE, area_id=kitchen.id)
    _register_sensor(entity_reg, "test", "kt_hum", SensorDeviceClass.HUMIDITY, area_id=kitchen.id)
    bt = _register_sensor(entity_reg, "test", "bd_temp", SensorDeviceClass.TEMPERATURE, area_id=bedroom.id)
    _register_sensor(entity_reg, "test", "bd_hum", SensorDeviceClass.HUMIDITY, area_id=bedroom.id)

    result = await _start_flow(hass)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"next_step_id": "discover"}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_DISCOVER_BY: DISCOVER_BY_AREA}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_DISCOVER_SELECTION: [kt.entity_id, bt.entity_id]},
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY

    # The import flows for additional entries run on the next tick
    await hass.async_block_till_done()
    entries = hass.config_entries.async_entries(DOMAIN)
    assert len(entries) == 2


async def test_discover_skips_already_configured(hass: HomeAssistant) -> None:
    """Temperature entities already in an entry are excluded from discovery."""
    area_reg = ar.async_get(hass)
    entity_reg = er.async_get(hass)

    living_room = area_reg.async_create("Living Room")
    temp = _register_sensor(entity_reg, "test", "lr_temp", SensorDeviceClass.TEMPERATURE, area_id=living_room.id)
    _register_sensor(entity_reg, "test", "lr_hum", SensorDeviceClass.HUMIDITY, area_id=living_room.id)

    # Pre-configure an entry using the temperature entity
    MockConfigEntry(
        domain=DOMAIN,
        data={CONF_SETUP_TYPE: SETUP_TYPE_MANUAL, CONF_TEMPERATURE: temp.entity_id, CONF_HUMIDITY: "sensor.other"},
    ).add_to_hass(hass)

    result = await _start_flow(hass)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"next_step_id": "discover"}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_DISCOVER_BY: DISCOVER_BY_AREA}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "discover_by"
    assert result["errors"] == {CONF_DISCOVER_BY: "no_devices_found"}


async def test_discover_by_device_creates_entry(hass: HomeAssistant) -> None:
    """Selecting a device pair creates a config entry named after the device."""
    device_reg = dr.async_get(hass)
    entity_reg = er.async_get(hass)

    # Device registry requires a real config entry to link against
    owner_entry = MockConfigEntry(domain="test")
    owner_entry.add_to_hass(hass)

    device = device_reg.async_get_or_create(
        config_entry_id=owner_entry.entry_id,
        identifiers={("test", "weather_station_1")},
        name="Weather Station",
    )
    temp = _register_sensor(entity_reg, "test", "ws_temp", SensorDeviceClass.TEMPERATURE, device_id=device.id)
    hum = _register_sensor(entity_reg, "test", "ws_hum", SensorDeviceClass.HUMIDITY, device_id=device.id)

    result = await _start_flow(hass)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"next_step_id": "discover"}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_DISCOVER_BY: DISCOVER_BY_DEVICE}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_DISCOVER_SELECTION: [temp.entity_id]}
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "Weather Station"
    assert result["data"][CONF_TEMPERATURE] == temp.entity_id
    assert result["data"][CONF_HUMIDITY] == hum.entity_id


async def test_import_step_creates_entry_without_ui(hass: HomeAssistant) -> None:
    """async_step_import creates an entry directly from data without showing a form."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_IMPORT},
        data={
            CONF_SETUP_TYPE: SETUP_TYPE_MANUAL,
            CONF_TEMPERATURE: TEST_TEMP,
            CONF_HUMIDITY: TEST_HUMIDITY,
            CONF_NAME: "Imported Room",
        },
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "Imported Room"
    assert result["data"][CONF_TEMPERATURE] == TEST_TEMP


async def test_options_flow_for_discover_entry_uses_manual_config_step(hass: HomeAssistant) -> None:
    """Options flow for a discover-created entry opens manual_config (not a non-existent discover step)."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_SETUP_TYPE: SETUP_TYPE_DISCOVER,
            CONF_TEMPERATURE: TEST_TEMP,
            CONF_HUMIDITY: TEST_HUMIDITY,
            CONF_NAME: "Kitchen",
        },
        title="Kitchen",
    )
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "manual_config"

    schema = result["data_schema"].schema
    temp_key = next(k for k in schema if k == CONF_TEMPERATURE)
    assert temp_key.default() == TEST_TEMP


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
