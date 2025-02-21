# NOTICE

Life360 has aggressively pushed the home automation community away by actively preventing access to their platform.

There is no reliable way to extract Life360 data - and my strong suggestion is to find a better product that embraces their community rather than pushing it away like @life360 do.

# Trackimo for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs) [![GitHub Stars](https://img.shields.io/github/stars/troykelly/hacs-trackimo.svg)](https://github.com/troykelly/hacs-trackimo/stargazers) [![GitHub Issues](https://img.shields.io/github/issues/troykelly/hacs-trackimo.svg)](https://github.com/troykelly/hacs-trackimo/issues) [![Current Version](https://img.shields.io/badge/version-0.0.22-green.svg)](https://github.com/troykelly/hacs-trackimo) [![Validate](https://github.com/troykelly/hacs-trackimo/actions/workflows/validate.yml/badge.svg?branch=main)](https://github.com/troykelly/hacs-trackimo/actions/workflows/validate.yml)

A simple Trackimo integration for Home Assistant. Allows you to see where your Trackimo devices are.

## Device

```yaml
source_type: gps
battery_level: 99
latitude: -27.468030
longitude: 153.039900
gps_accuracy: 100
altitude: 60
bearing: null
speed: null
mps: null
timestamp: 1570775634
address: Brisbane River, Brisbane, Queensland, Australia
country: Australia
city: Brisbane City
state: Queensland
region: null
street: Brisbane River
attribution: Data © OpenStreetMap contributors, ODbL 1.0. https://osm.org/copyright
age: 31349542
friendly_name: My Car
icon: mdi:map-marker-radius
```

## Buy me a coffee

If this helps you, or you are just generous. I do love coffee.

<a href="https://buymeacoff.ee/troykelly" target="_blank"><img src="https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png" alt="Buy Me A Coffee" style="height: auto !important;width: auto !important;" ></a>

---

## Features

- Get all Trackimo Devices
- Track Them

---

## Setup

Add the integration.

Supply your Trackimo Username and Passowrd

---

## Usage

Once connected, your Trackimo devices will appear as `device_tracker.device_name`

---

## Contributions

PR's are more than welcome either to the HACS component or the Trackimo Library.

### Thanks to:

<a href="https://github.com/hwikene" target="_blank"><img src="https://avatars3.githubusercontent.com/u/17985923?s=460&u=26ef329676c71af07fb01916f4ff553d88bfb94a&v=4" alt="hwikene on GitHub" width="50"/>@hwikene</a> for Norwegian translation

---
