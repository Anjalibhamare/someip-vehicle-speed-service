"""Vehicle ECU: SOME/IP service provider.
Provides GetSpeed/GetVehicleState methods and SpeedChanged/OverspeedWarning events.
Run: python -m src.vehicle_ecu.server
"""
import asyncio
import logging
from someipy import MessageType, Method, MethodResult, ReturnCode, ServerServiceInstance, ServiceBuilder, TransportLayerProtocol, connect_to_someipy_daemon
from someipy.someipy_logging import set_someipy_log_level
from src.common.logic import OVERSPEED_LIMIT_KMPH, is_overspeed, vehicle_state_from_speed
from src.common.vehicle_interface import GET_SPEED_METHOD_ID, GET_VEHICLE_STATE_METHOD_ID, LOOPBACK_IP, OVERSPEED_EVENTGROUP_ID, OVERSPEED_WARNING_EVENT_ID, SPEED_CHANGED_EVENT_ID, SPEED_EVENTGROUP_ID, VEHICLE_INSTANCE_ID, VEHICLE_PROVIDER_PORT, VEHICLE_SERVICE_ID, VEHICLE_MAJOR_VERSION, SpeedPayload, VehicleStatePayload, overspeed_eventgroup, speed_eventgroup

logging.basicConfig(level=logging.INFO, format="%(asctime)s | VEHICLE-ECU | %(levelname)s | %(message)s")
logger = logging.getLogger("vehicle_ecu")
SPEED_DEMO_SEQUENCE = (0, 20, 40, 60, 80, 90, 100, 70, 50, 30)
current_speed_kmph = 0


def method_response(payload: bytes, return_code=ReturnCode.E_OK) -> MethodResult:
    result = MethodResult()
    result.message_type = MessageType.RESPONSE
    result.return_code = return_code
    result.payload = payload
    return result


async def get_speed_handler(_input_data: bytes, client_address) -> MethodResult:
    logger.info("GetSpeed request from %s -> %d km/h", client_address, current_speed_kmph)
    return method_response(SpeedPayload(current_speed_kmph).serialize())


async def get_vehicle_state_handler(_input_data: bytes, client_address) -> MethodResult:
    state = vehicle_state_from_speed(current_speed_kmph)
    label = "STOPPED" if state == 0 else "MOVING"
    logger.info("GetVehicleState request from %s -> %s", client_address, label)
    return method_response(VehicleStatePayload(state).serialize())


def build_provider_service():
    get_speed = Method(id=GET_SPEED_METHOD_ID, protocol=TransportLayerProtocol.UDP, method_handler=get_speed_handler)
    get_state = Method(id=GET_VEHICLE_STATE_METHOD_ID, protocol=TransportLayerProtocol.UDP, method_handler=get_vehicle_state_handler)
    return (ServiceBuilder().with_service_id(VEHICLE_SERVICE_ID).with_major_version(VEHICLE_MAJOR_VERSION)
            .with_method(get_speed).with_method(get_state).with_eventgroup(speed_eventgroup)
            .with_eventgroup(overspeed_eventgroup).build())


async def publish_vehicle_updates(service_instance: ServerServiceInstance) -> None:
    global current_speed_kmph
    index = 0
    while True:
        current_speed_kmph = SPEED_DEMO_SEQUENCE[index]
        index = (index + 1) % len(SPEED_DEMO_SEQUENCE)
        service_instance.send_event(SPEED_EVENTGROUP_ID, SPEED_CHANGED_EVENT_ID, SpeedPayload(current_speed_kmph).serialize())
        logger.info("Published SpeedChanged: %d km/h", current_speed_kmph)
        if is_overspeed(current_speed_kmph):
            service_instance.send_event(OVERSPEED_EVENTGROUP_ID, OVERSPEED_WARNING_EVENT_ID, SpeedPayload(current_speed_kmph).serialize())
            logger.warning("OVERSPEED WARNING published: %d km/h (limit: %d km/h)", current_speed_kmph, OVERSPEED_LIMIT_KMPH)
        await asyncio.sleep(2)


async def main() -> None:
    set_someipy_log_level(logging.INFO)
    logger.info("Starting Vehicle ECU provider")
    daemon = await connect_to_someipy_daemon()
    service_instance = ServerServiceInstance(daemon=daemon, service=build_provider_service(), instance_id=VEHICLE_INSTANCE_ID, endpoint_ip=LOOPBACK_IP, endpoint_port=VEHICLE_PROVIDER_PORT, ttl=5, cyclic_offer_delay_ms=2000)
    await service_instance.start_offer()
    logger.info("VehicleSpeedService offered | Service ID=0x%04X | %s:%d", VEHICLE_SERVICE_ID, LOOPBACK_IP, VEHICLE_PROVIDER_PORT)
    publisher_task = asyncio.create_task(publish_vehicle_updates(service_instance))
    try:
        await asyncio.Future()
    finally:
        publisher_task.cancel()
        try:
            await publisher_task
        except asyncio.CancelledError:
            pass
        await service_instance.stop_offer()
        await daemon.disconnect_from_daemon()
        logger.info("Vehicle ECU stopped cleanly")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nVehicle ECU stopped by user.")
