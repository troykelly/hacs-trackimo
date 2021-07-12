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
    EVENT_MAINTENANCE,
    EVENT_TEXT_MESSAGE,
    TRACKER_UPDATE,
    MANUFACTURER,
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
                    EVENT_ALL_EVENTS,
                )
            ],
        ),
    }
)


async def async_setup_entry(hass: HomeAssistantType, entry, async_add_entities):
    """Configure a dispatcher connection based on a config entry."""

    api = hass.data[DOMAIN][entry.entry_id]

    if not "entity_ref" in hass.data[DOMAIN]:
        hass.data[DOMAIN]["entity_ref"] = {}

    if not "tasks" in hass.data[DOMAIN]:
        hass.data[DOMAIN]["tasks"] = {}

    entities = []
    for device_id in api.devices:
        device = api.devices[device_id]
        if device and device.latitude and device.longitude:
            hass.data[DOMAIN]["entity_ref"][device_id] = TrackimoEntity(device)
            entities.append(hass.data[DOMAIN]["entity_ref"][device_id])

    def device_event_handler(event_type=None, device_id=None, device=None, ts=None):
        if not (event_type and device):
            _LOGGER.warning("Event received with no type or device")
            return None
        _LOGGER.debug("%s event received: %d", event_type, device_id)
        try:
            hass.data[DOMAIN]["entity_ref"][device.id].async_device_changed()
        except Exception as err:
            _LOGGER.error("Unable to send update to HA")
            _LOGGER.exception(err)
            raise err

    async_add_entities(entities)

    hass.data[DOMAIN]["tasks"]["device_tracker"] = api.track(
        interval=SCAN_INTERVAL, event_receiver=device_event_handler
    )


class TrackimoEntity(TrackerEntity, RestoreEntity):
    """Represent a trackimo device."""

    def __init__(
        self,
        device,
    ):
        """Set up Trackimo entity."""
        self.__device = device

    def async_device_changed(self):
        """Send changed data to HA"""
        _LOGGER.debug("%s (%d) advising HA of update", self.name, self.unique_id)
        self.async_schedule_update_ha_state()

    @property
    def device_info(self):
        """Return the device_info of the device."""
        return {
            "identifiers": {(DOMAIN, self.unique_id)},
            "name": self.name,
            "model": trackimo_device_type(self.__device.features.id),
            "sw_version": getattr(self.__device.features,'firmware', 'unknown'),
            "manufacturer": MANUFACTURER,
        }

    @property
    def should_poll(self):
        return False

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
        return 20 if self.__device.triangulated else 100

    @property
    def name(self):
        """Return the name of the device."""
        return self.__device.name

    @property
    def unique_id(self):
        """Return the unique ID."""
        return self.__device.id

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


def trackimo_device_type(device_feature_id=None):
    """Convert Trackimo Feature ID to Device Name

    Attributes:
        device_feature_id (int): Feature ID from device
    """

    if not device_feature_id:
        return "Unknown Device"
    if device_feature_id == 16:
        return "3G GPS Watch"
    if device_feature_id == 13:
        return "3G GPS Guardian"
    if device_feature_id == 12:
        return "3G GPS Universal"
    return "Unknown Type " + str(device_feature_id)
