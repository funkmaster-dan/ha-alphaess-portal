"""Shared device metadata."""
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

class PortalEntity(CoordinatorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        serial = coordinator.entry.data['serial']
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, serial)}, manufacturer='AlphaESS', name=f'AlphaESS Portal {serial}', model='Portal-controlled ESS', configuration_url='https://portal.alphaess.com/')

    @property
    def power(self):
        return (self.coordinator.data or {}).get('power', {})
