"""SOME/IP interface shared by the Vehicle ECU and its consumers."""

from dataclasses import dataclass

from someipy import Event, EventGroup, Method, ServiceBuilder, TransportLayerProtocol
from someipy.serialization import SomeIpPayload, Uint8, Uint16

from src.common.logic import VEHICLE_MOVING, VEHICLE_STOPPED

VEHICLE_SERVICE_ID = 0x1234
VEHICLE_INSTANCE_ID = 0x5678
VEHICLE_MAJOR_VERSION = 1
GET_SPEED_METHOD_ID = 0x0001
GET_VEHICLE_STATE_METHOD_ID = 0x0002
SPEED_CHANGED_EVENT_ID = 0x8001
OVERSPEED_WARNING_EVENT_ID = 0x8002
SPEED_EVENTGROUP_ID = 0x0001
OVERSPEED_EVENTGROUP_ID = 0x0002
LOOPBACK_IP = "127.0.0.1"
VEHICLE_PROVIDER_PORT = 3000
CLUSTER_CLIENT_PORT = 3002
CENTRAL_VEHICLE_CLIENT_PORT = 3004


@dataclass
class SpeedPayload(SomeIpPayload):
    """Vehicle speed as an unsigned 16-bit value in km/h."""
    speed_kmph: Uint16

    def __init__(self, speed_kmph: int = 0):
        if not 0 <= speed_kmph <= 65535:
            raise ValueError("Speed must fit in an unsigned 16-bit value")
        self.speed_kmph = Uint16(speed_kmph)


@dataclass
class VehicleStatePayload(SomeIpPayload):
    """Vehicle state: 0 = STOPPED, 1 = MOVING."""
    state: Uint8

    def __init__(self, state: int = VEHICLE_STOPPED):
        if state not in (VEHICLE_STOPPED, VEHICLE_MOVING):
            raise ValueError("Vehicle state must be STOPPED(0) or MOVING(1)")
        self.state = Uint8(state)


get_speed_method = Method(id=GET_SPEED_METHOD_ID, protocol=TransportLayerProtocol.UDP)
get_vehicle_state_method = Method(id=GET_VEHICLE_STATE_METHOD_ID, protocol=TransportLayerProtocol.UDP)
speed_changed_event = Event(id=SPEED_CHANGED_EVENT_ID, protocol=TransportLayerProtocol.UDP)
overspeed_warning_event = Event(id=OVERSPEED_WARNING_EVENT_ID, protocol=TransportLayerProtocol.UDP)
speed_eventgroup = EventGroup(id=SPEED_EVENTGROUP_ID, events=[speed_changed_event])
overspeed_eventgroup = EventGroup(id=OVERSPEED_EVENTGROUP_ID, events=[overspeed_warning_event])
vehicle_service = (
    ServiceBuilder().with_service_id(VEHICLE_SERVICE_ID)
    .with_major_version(VEHICLE_MAJOR_VERSION)
    .with_method(get_speed_method).with_method(get_vehicle_state_method)
    .with_eventgroup(speed_eventgroup).with_eventgroup(overspeed_eventgroup).build()
)
