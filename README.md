*Please :star: this repo if you find it useful*

# Sensor of Apparent Temperature for Home Assistant

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]][license]

[![hacs][hacs-shield]][hacs]
[![Project Maintenance][maintenance-shield]][user_profile]

[![Community Forum][forum-shield]][forum]

## Installation

### Install from HACS (recommended)

1. Have [HACS][hacs] installed, this will allow you to easily manage and track updates.
1. Add this repository as a custom repository in HACS:\
[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)][hacs-repository]
1. Search in HACS for "Apparent Temperature" and click Install.

... then if you want to use `configuration.yaml` to configure sensor...
1. Add `apparent_temperature` sensor to your `configuration.yaml` file. See configuration examples below.
1. Restart Home Assistant

### Manual installation

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
1. If you do not have a `custom_components` directory (folder) there, you need to create it.
1. In the `custom_components` directory (folder) create a new folder called `apparent_temperature`.
1. Download file `apparent_temperature.zip` from the [latest release section][releases-latest] in this repository.
1. Extract _all_ files from this archive you downloaded in the directory (folder) you created.
1. Restart Home Assistant

... then if you want to use `configuration.yaml` to configure sensor...
1. Add `apparent_temperature` sensor to your `configuration.yaml` file. See configuration examples below.
1. Restart Home Assistant

### Configuration Examples

#### Weather Entity Example

```yaml
# Example configuration.yaml entry
sensor:
  - platform: apparent_temperature
    source: weather.home
```

#### Independent Temperature and Humidity Entities Example

```yaml
# Example configuration.yaml entry
sensor:
  - platform: apparent_temperature
    name: 'Basement Feels Like Temperature'
    source:
      - sensor.basement_temperature
      - sensor.basement_humidity
```

### Configuration Variables

**source:**\
  _(string | list of strings) (Required)_\
  Weather provider entity ID or climate entity ID or list of sensors entity IDs.\
  For calculations sensor uses temperature, humidity and wind speed values. Temperature and humidity values is required. Wind speed value is optional.\
  Weather provider provide all values. Climate object provide only temperature and humidity.

> **_Note_**:\
> You can use groups of entities as a data source. These groups will be automatically expanded to individual entities.

> **_Note_**:\
> If you specify several sources of the same type of data (for example, a weather provider and a separate temperature sensor), the sensor uses only one of them as a source (the one that will be the last in the list). Therefore, the result of calculations can be unpredictable.

**name:**\
  _(string) (Optional) (Default value: name of first source + " Apparent Temperature")_\
  Name to use in the frontend.

**unique_id**\
  _(string) (Optional)_\
  An ID that uniquely identifies this sensor. Set this to a unique value to allow customization through the UI.

> **_Note_**:
> You can use site [uuidgenerator.net](https://www.uuidgenerator.net/) to generate unique ID's.

## Track updates

You can automatically track new versions of this component and update it by [HACS][hacs].

## Troubleshooting

To enable debug logs use this configuration:
```yaml
# Example configuration.yaml entry
logger:
  default: info
  logs:
    custom_components.apparent_temperature: debug
```
... then restart HA.

## Contributions are welcome!

This is an active open-source project. We are always open to people who want to
use the code or contribute to it.

We have set up a separate document containing our
[contribution guidelines](CONTRIBUTING.md).

Thank you for being involved! :heart_eyes:

## Authors & contributors

This is a fork of [Limych/ha-apparent-temperature](https://github.com/Limych/ha-apparent-temperature) with additional features including a UI config flow and auto-discovery of room sensors.

The original component was created by [Andrey "Limych" Khrolenok](https://github.com/Limych).

For a full list of all authors and contributors,
check [the contributor's page][contributors].

## License

creative commons Attribution-NonCommercial-ShareAlike 4.0 International License

See separate [license file](LICENSE.md) for full text.

***

[component]: https://github.com/JoeWells/ha-apparent-temperature
[commits-shield]: https://img.shields.io/github/commit-activity/y/JoeWells/ha-apparent-temperature.svg?style=popout
[commits]: https://github.com/JoeWells/ha-apparent-temperature/commits/dev
[hacs-shield]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=popout
[hacs]: https://hacs.xyz
[hacs-repository]: https://my.home-assistant.io/redirect/hacs_repository/?owner=JoeWells&repository=ha-apparent-temperature&category=integration
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=popout
[forum]: https://community.home-assistant.io/t/sensor-of-temperature-feels-like/299063
[license]: https://github.com/JoeWells/ha-apparent-temperature/blob/main/LICENSE.md
[license-shield]: https://img.shields.io/badge/license-Creative_Commons_BY--NC--SA_License-lightgray.svg?style=popout
[maintenance-shield]: https://img.shields.io/badge/maintainer-Joe%20Wells%20%40JoeWells-blue.svg?style=popout
[releases-shield]: https://img.shields.io/github/release/JoeWells/ha-apparent-temperature.svg?style=popout
[releases]: https://github.com/JoeWells/ha-apparent-temperature/releases
[releases-latest]: https://github.com/JoeWells/ha-apparent-temperature/releases/latest
[user_profile]: https://github.com/JoeWells
[report_bug]: https://github.com/JoeWells/ha-apparent-temperature/issues/new?template=bug_report.md
[suggest_idea]: https://github.com/JoeWells/ha-apparent-temperature/issues/new?template=feature_request.md
[contributors]: https://github.com/JoeWells/ha-apparent-temperature/graphs/contributors
