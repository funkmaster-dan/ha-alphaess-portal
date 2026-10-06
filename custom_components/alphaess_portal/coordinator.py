"""Poll portal telemetry once for all entities."""
from datetime import timedelta
from aiohttp import ClientError
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .client import PortalAuthError
from .const import DEFAULTS
import logging

class PortalCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, entry, client):
        super().__init__(hass, logging.getLogger(__name__), name='AlphaESS Portal', config_entry=entry, update_interval=timedelta(seconds=30))
        self.entry, self.client = entry, client

    def setting(self, key):
        return self.entry.options.get(key, DEFAULTS[key])

    async def _async_update_data(self):
        try:
            return await self.client.status()
        except PortalAuthError as exc:
            raise ConfigEntryAuthFailed('Portal authentication failed') from exc
        except (RuntimeError, ClientError, TimeoutError) as exc:
            raise UpdateFailed('Cannot read AlphaESS portal') from exc
