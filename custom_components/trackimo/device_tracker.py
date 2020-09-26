"""Support for Trackimo device tracking."""
from datetime import datetime, timedelta
import logging

import async_timeout

import voluptuous as vol

from homeassistant.components.device_tracker import PLATFORM_SCHEMA, SOURCE_TYPE_GPS
from homeassistant.components.device_tracker.config_entry import TrackerEntity
from homeassistant.const import (
    CONF_EVENT,
    CONF_MONITORED_CONDITIONS,
    CONF_SCAN_INTERVAL,
)
from homeassistant.core import callback
from homeassistant.helpers import device_registry
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.typing import HomeAssistantType
from homeassistant.util import slugify

from . import DOMAIN
from .const import (
    ATTR_ACCURACY,
    ATTR_ADDRESS,
    ATTR_AGE,
    ATTR_COUNTRY,
    ATTR_CITY,
    ATTR_STATE,
    ATTR_REGION,
    ATTR_STREET,
    ATTR_ALTITUDE,
    ATTR_BATTERY,
    ATTR_BEARING,
    ATTR_CATEGORY,
    ATTR_GEOFENCE,
    ATTR_LATITUDE,
    ATTR_LONGITUDE,
    ATTR_MOTION,
    ATTR_SPEED,
    ATTR_SPEEDMPS,
    ATTR_STATUS,
    ATTR_TIMESTAMP,
    ATTR_ATTRIBUTION,
    CONF_MAX_ACCURACY,
    CONF_SKIP_ACCURACY_ON,
    EVENT_ALARM,
    EVENT_ALL_EVENTS,
    EVENT_COMMAND_RESULT,
    EVENT_DEVICE_FUEL_DROP,
    EVENT_DEVICE_MOVING,
    EVENT_DEVICE_OFFLINE,
    EVENT_DEVICE_ONLINE,
    EVENT_DEVICE_OVERSPEED,
    EVENT_DEVICE_STOPPED,
    EVENT_DEVICE_UNKNOWN,
    EVENT_GEOFENCE_ENTER,
    EVENT_GEOFENCE_EXIT,
    EVENT_IGNITION_OFF,
    EVENT_IGNITION_ON,
    EVENT_MAINTENANCE,
    EVENT_TEXT_MESSAGE,
    TRACKER_UPDATE,
)

_LOGGER = logging.getLogger(__name__)

DEFAULT_SCAN_INTERVAL = timedelta(seconds=30)
SCAN_INTERVAL = DEFAULT_SCAN_INTERVAL

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_MAX_ACCURACY, default=0): vol.All(
            vol.Coerce(int), vol.Range(min=0)
        ),
        vol.Optional(CONF_SKIP_ACCURACY_ON, default=[]): vol.All(
            cv.ensure_list, [cv.string]
        ),
        vol.Optional(CONF_MONITORED_CONDITIONS, default=[]): vol.All(
            cv.ensure_list, [cv.string]
        ),
        vol.Optional(CONF_EVENT, default=[]): vol.All(
            cv.ensure_list,
            [
                vol.Any(
                    EVENT_DEVICE_MOVING,
                    EVENT_COMMAND_RESULT,
                    EVENT_DEVICE_FUEL_DROP,
                    EVENT_GEOFENCE_ENTER,
                    EVENT_DEVICE_OFFLINE,
                    EVENT_GEOFENCE_EXIT,
                    EVENT_DEVICE_OVERSPEED,
                    EVENT_DEVICE_ONLINE,
                    EVENT_DEVICE_STOPPED,
                    EVENT_MAINTENANCE,
                    EVENT_ALARM,
                    EVENT_TEXT_MESSAGE,
                    EVENT_DEVICE_UNKNOWN,
                    EVENT_IGNITION_OFF,
                    EVENT_IGNITION_ON,
                    EVENT_ALL_EVENTS,
                )
            ],
        ),
    }
)


async def async_setup_entry(hass: HomeAssistantType, entry, async_add_entities):
    """Configure a dispatcher connection based on a config entry."""

    api = hass.data[DOMAIN][entry.entry_id]

    entities = []
    for device_id in api.devices:
        device = api.devices[device_id]
        if device and device.latitude and device.longitude:
            entity = TrackimoEntity(device)
            entities.append(entity)

    async_add_entities(entities)


class TrackimoEntity(TrackerEntity, RestoreEntity):
    """Represent a trackimo device."""

    def __init__(
        self,
        device,
    ):
        """Set up Trackimo entity."""
        self.__device = device

    @property
    def should_poll(self):
        return True

    @property
    def icon(self):
        return (
            "mdi:map-marker" if self.__device.triangulated else "mdi:map-marker-radius"
        )

    @property
    def battery_level(self):
        """Return battery value of the device."""
        return self.__device.battery

    @property
    def device_state_attributes(self):
        """Return device specific attributes."""
        return {
            ATTR_ALTITUDE: self.__device.altitude,
            ATTR_BEARING: None,
            ATTR_SPEED: self.__device.speedKMH,
            ATTR_SPEEDMPS: self.__device.speedMPS,
            ATTR_TIMESTAMP: self.__device.updated.timestamp(),
            ATTR_ADDRESS: self.__device.address,
            ATTR_COUNTRY: self.__device.country,
            ATTR_CITY: self.__device.city,
            ATTR_STATE: self.__device.state,
            ATTR_REGION: self.__device.region,
            ATTR_STREET: self.__device.street,
            ATTR_ATTRIBUTION: self.__device.attribution,
            ATTR_AGE: self.__device.age,
        }

    @property
    def latitude(self):
        """Return latitude value of the device."""
        return self.__device.latitude

    @property
    def longitude(self):
        """Return longitude value of the device."""
        return self.__device.longitude

    @property
    def location_accuracy(self):
        """Return the gps accuracy of the device."""
        return 20 if self.__device.triangulated else 200

    @property
    def name(self):
        """Return the name of the device."""
        return self.__device.name

    @property
    def unique_id(self):
        """Return the unique ID."""
        return self.__device.id

    @property
    def device_info(self):
        """Return the device info."""
        return {"name": self.__device.name, "identifiers": {(DOMAIN, self.__device.id)}}

    @property
    def source_type(self):
        """Return the source type, eg gps or router, of the device."""
        return SOURCE_TYPE_GPS

    async def async_update(self):
        """Update Trackimo Data"""
        await self.__device.refresh()

    async def async_added_to_hass(self):
        """Register state update callback."""
        await super().async_added_to_hass()

    async def async_will_remove_from_hass(self):
        """Clean up after entity before removal."""
        await super().async_will_remove_from_hass()