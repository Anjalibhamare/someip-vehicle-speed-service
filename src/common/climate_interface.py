"""SOME/IP interface shared by the Climate ECU and Central Display."""

from dataclasses import dataclass

from someipy import Event, EventGroup, Method, ServiceBuilder, TransportLayerProtocol
from someipy.serialization import SomeIpPayload, Sint16, Uint8

CLIMATE_SERVICE_ID = 0x2234
CLIMATE_INSTANCE_ID = 0x0001
CLIMATE_MAJOR_VERSION = 1
GET_CABIN_TEMPERATURE_METHOD_ID = 0x0001
SET_TARGET_TEMPERATURE_METHOD_ID = 0x0002
CABIN_TEMPERATURE_CHANGED_EVENT_ID = 0x8001
CABIN_TEMPERATURE_EVENTGROUP_ID = 0x0001
TARGET_ACCEPTED = 0
TARGET_REJECTED = 1
CLIMATE_PROVIDER_PORT = 3001
CENTRAL_CLIMATE_CLIENT_PORT = 3006


@dataclass
class CabinTemperaturePayload(SomeIpPayload):
    """Measured cabin temperature in tenths of a degree C."""
    temperature_tenths_c: Sint16

    def __init__(self, temperature_tenths_c: int = 240):
        self.temperature_tenths_c = Sint16(temperature_tenths_c)


@dataclass
class TargetTemperaturePayload(SomeIpPayload):
    """Requested target temperature in tenths of a degree C."""
    temperature_tenths_c: Sint16

    def __init__(self, temperature_tenths_c: int = 220):
        self.temperature_tenths_c = Sint16(temperature_tenths_c)


@dataclass
class TargetTemperatureStatusPayload(SomeIpPayload):
    """0 = accepted, 1 = rejected by application temperature limits."""
    status: Uint8

    def __init__(self, status: int = TARGET_ACCEPTED):
        self.status = Uint8(status)


get_cabin_temperature_method = Method(id=GET_CABIN_TEMPERATURE_METHOD_ID, protocol=TransportLayerProtocol.UDP)
set_target_temperature_method = Method(id=SET_TARGET_TEMPERATURE_METHOD_ID, protocol=TransportLayerProtocol.UDP)
cabin_temperature_changed_event = Event(id=CABIN_TEMPERATURE_CHANGED_EVENT_ID, protocol=TransportLayerProtocol.UDP)
cabin_temperature_eventgroup = EventGroup(id=CABIN_TEMPERATURE_EVENTGROUP_ID, events=[cabin_temperature_changed_event])
climate_service = (
    ServiceBuilder().with_service_id(CLIMATE_SERVICE_ID)
    .with_major_version(CLIMATE_MAJOR_VERSION)
    .with_method(get_cabin_temperature_method).with_method(set_target_temperature_method)
    .with_eventgroup(cabin_temperature_eventgroup).build()
)
