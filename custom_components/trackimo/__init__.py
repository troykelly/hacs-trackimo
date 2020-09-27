"""The Trackimo integration."""
import asyncio

import voluptuous as vol
import logging

from homeassistant import exceptions
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.components.device_tracker import DOMAIN as DEVICE_TRACKER

from trackimo import Trackimo

from .const import DOMAIN

CONFIG_SCHEMA = vol.Schema({DOMAIN: vol.Schema({})}, extra=vol.ALLOW_EXTRA)

PLATFORMS = [DEVICE_TRACKER]


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Trackimo component."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Trackimo from a config entry."""

    if not DOMAIN in hass.data:
        hass.data[DOMAIN] = {}

    client_id = entry.data["clientid"] if "clientid" in entry.data else None
    client_secret = entry.data["clientsecret"] if "clientsecret" in entry.data else None
    username = entry.data["username"] if "username" in entry.data else None
    password = entry.data["password"] if "password" in entry.data else None

    hass.data[DOMAIN][entry.entry_id] = Trackimo(
        loop=hass.loop, client_id=client_id, client_secret=client_secret
    )

    if client_id and client_secret and username and password:
        if not await hass.data[DOMAIN][entry.entry_id].login(
            username,
            password,
        ):
            raise CannotConnect

    for component in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, component)
        )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in PLATFORMS
            ]
        )
    )
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""
