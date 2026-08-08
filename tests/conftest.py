"""Common test fixtures and mocks."""
import sys
from unittest.mock import MagicMock


class _MockCoordinatorEntity:
    """Minimal base for CoordinatorEntity."""
    def __init__(self, *args, **kwargs):
        self.coordinator = args[0] if args else kwargs.get("coordinator")
    @property
    def available(self):
        return True
    def async_write_ha_state(self):
        pass
    def async_remove(self):
        pass


class _MockSensorEntity:
    """Minimal base for SensorEntity."""
    pass


class _MockDataUpdateCoordinator:
    """Minimal base for DataUpdateCoordinator with needed methods."""
    def __init__(self, *args, **kwargs):
        self.hass = MagicMock()
        self.data = None
        self.last_update_success = True
        self.name = kwargs.get("name")
    def async_set_updated_data(self, data):
        self.data = data
    def async_add_listener(self, *args, **kwargs):
        return lambda: None
    def async_config_entry_first_refresh(self):
        pass


# Mock homeassistant modules before any imports
sys.modules['homeassistant'] = MagicMock()
sys.modules['homeassistant.config_entries'] = MagicMock()
sys.modules['homeassistant.core'] = MagicMock()
sys.modules['homeassistant.data_entry_flow'] = MagicMock()
sys.modules['homeassistant.exceptions'] = MagicMock()
sys.modules['homeassistant.helpers'] = MagicMock()
sys.modules['homeassistant.helpers.aiohttp_client'] = MagicMock()
sys.modules['homeassistant.helpers.config_validation'] = MagicMock()
sys.modules['homeassistant.helpers.update_coordinator'] = MagicMock()
sys.modules['homeassistant.helpers.entity_platform'] = MagicMock()
sys.modules['homeassistant.helpers.storage'] = MagicMock()
sys.modules['homeassistant.components'] = MagicMock()
sys.modules['homeassistant.components.sensor'] = MagicMock()
sys.modules['homeassistant.const'] = MagicMock()
sys.modules['aioimaplib'] = MagicMock()

sys.modules['homeassistant.helpers.update_coordinator'].CoordinatorEntity = _MockCoordinatorEntity
sys.modules['homeassistant.helpers.update_coordinator'].DataUpdateCoordinator = _MockDataUpdateCoordinator
sys.modules['homeassistant.components.sensor'].SensorEntity = _MockSensorEntity

sys.modules['homeassistant.const'].Platform = MagicMock()
sys.modules['homeassistant.const'].Platform.SENSOR = "sensor"
