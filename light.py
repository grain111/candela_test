"""Platform for light integration."""
from __future__ import annotations

import logging

from .candela_v2 import Lamp
import voluptuous as vol

from pprint import pformat

# Import the device class from the component that you want to support
import homeassistant.helpers.config_validation as cv
from homeassistant.components.light import (SUPPORT_BRIGHTNESS, ATTR_BRIGHTNESS,
                                            PLATFORM_SCHEMA, LightEntity)
from homeassistant.const import CONF_NAME, CONF_MAC
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.components import bluetooth

_LOGGER = logging.getLogger("yealight_candela_test")

# Validation of the user's configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME): cv.string,
    vol.Required(CONF_MAC): cv.string,
})


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None
) -> None:
    """Set up the Godox Light platform."""
    # Add devices
    _LOGGER.info(pformat(config))
    
    light = {
        "name": config[CONF_NAME],
        "mac": config[CONF_MAC]
    }

    device = bluetooth.async_ble_device_from_address(hass, light["mac"], connectable=True)
    
    async_add_entities([CandelaLight(device, light["name"])])

class CandelaLight(LightEntity):
    """Representation of an Godox Light."""

    def __init__(self, device, name) -> None:
        """Initialize an CandelaLight."""
        _LOGGER.info(pformat(device))
        self._mac = device.address
        self._light = Lamp(device)
        self._name = name
        self._state = None
        self._brightness = None

    @property
    def unique_id(self) -> str:
        # TODO: replace with _attr
        """Return the unique id of the light."""
        return self._mac

    @property
    def name(self) -> str:
        """Return the display name of this light."""
        return self._name

    @property
    def brightness(self):
        """Return the brightness of the light.
        This method is optional. Removing it indicates to Home Assistant
        that brightness is not supported for this light.
        """
        return self._brightness * 2.55

    @property
    def supported_features(self):
        return SUPPORT_BRIGHTNESS

    @property
    def is_on(self) -> bool | None:
        """Return true if light is on."""
        return self._state

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Instruct the light to turn on."""
        
        if ATTR_BRIGHTNESS in kwargs:
            brightness = kwargs[ATTR_BRIGHTNESS]
            brightness_dev = int(round(brightness * 1.0 / 255 * 100))
            await self._light.set_brightness(brightness_dev)
            
        await self._light.turn_on()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Instruct the light to turn off."""
        await self._light.turn_off()

    def update(self) -> None:
        """Fetch new state data for this light.
        This is the only method that should fetch new data for Home Assistant.
        """
        self._state = self._light.is_on
        self._brightness = self._light.brightness