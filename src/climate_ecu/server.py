"""Climate ECU SOME/IP provider for cabin temperature and target setting."""
import asyncio
import logging
from someipy import MessageType, Method, MethodResult, ReturnCode, ServerServiceInstance, ServiceBuilder, TransportLayerProtocol, connect_to_someipy_daemon
from someipy.someipy_logging import set_someipy_log_level
from src.common.logic import is_valid_target_temperature
from src.common.vehicle_interface import LOOPBACK_IP
from src.common.climate_interface import CABIN_TEMPERATURE_CHANGED_EVENT_ID, CABIN_TEMPERATURE_EVENTGROUP_ID, CLIMATE_INSTANCE_ID, CLIMATE_PROVIDER_PORT, CLIMATE_SERVICE_ID, CLIMATE_MAJOR_VERSION, GET_CABIN_TEMPERATURE_METHOD_ID, SET_TARGET_TEMPERATURE_METHOD_ID, TARGET_ACCEPTED, TARGET_REJECTED, CabinTemperaturePayload, TargetTemperaturePayload, TargetTemperatureStatusPayload, cabin_temperature_eventgroup

logging.basicConfig(level=logging.INFO, format="%(asctime)s | CLIMATE-ECU | %(levelname)s | %(message)s")
logger = logging.getLogger("climate_ecu")
current_cabin_temperature_tenths = 240
requested_target_temperature_tenths = 220


def method_response(payload: bytes, return_code=ReturnCode.E_OK) -> MethodResult:
    result = MethodResult()
    result.message_type = MessageType.RESPONSE
    result.return_code = return_code
    result.payload = payload
    return result


async def get_cabin_temperature_handler(_input_data: bytes, client_address) -> MethodResult:
    logger.info("GetCabinTemperature request from %s -> %.1f C", client_address, current_cabin_temperature_tenths / 10)
    return method_response(CabinTemperaturePayload(current_cabin_temperature_tenths).serialize())


async def set_target_temperature_handler(input_data: bytes, client_address) -> MethodResult:
    global requested_target_temperature_tenths
    try:
        request = TargetTemperaturePayload().deserialize(input_data)
        requested = int(request.temperature_tenths_c.value)
    except Exception as error:
        logger.warning("Malformed SetTargetTemperature request from %s: %s", client_address, error)
        return method_response(b"", ReturnCode.E_MALFORMED_MESSAGE)
    if is_valid_target_temperature(requested):
        requested_target_temperature_tenths = requested
        status = TARGET_ACCEPTED
        logger.info("Target temperature accepted from %s: %.1f C", client_address, requested / 10)
    else:
        status = TARGET_REJECTED
        logger.warning("Target temperature rejected from %s: %.1f C (valid range 16.0–30.0 C)", client_address, requested / 10)
    return method_response(TargetTemperatureStatusPayload(status).serialize())


def build_provider_service():
    get_temperature = Method(id=GET_CABIN_TEMPERATURE_METHOD_ID, protocol=TransportLayerProtocol.UDP, method_handler=get_cabin_temperature_handler)
    set_temperature = Method(id=SET_TARGET_TEMPERATURE_METHOD_ID, protocol=TransportLayerProtocol.UDP, method_handler=set_target_temperature_handler)
    return (ServiceBuilder().with_service_id(CLIMATE_SERVICE_ID).with_major_version(CLIMATE_MAJOR_VERSION)
            .with_method(get_temperature).with_method(set_temperature).with_eventgroup(cabin_temperature_eventgroup).build())


async def publish_temperature_updates(service_instance: ServerServiceInstance) -> None:
    global current_cabin_temperature_tenths
    while True:
        if current_cabin_temperature_tenths < requested_target_temperature_tenths:
            current_cabin_temperature_tenths = min(current_cabin_temperature_tenths + 5, requested_target_temperature_tenths)
        elif current_cabin_temperature_tenths > requested_target_temperature_tenths:
            current_cabin_temperature_tenths = max(current_cabin_temperature_tenths - 5, requested_target_temperature_tenths)
        payload = CabinTemperaturePayload(current_cabin_temperature_tenths).serialize()
        service_instance.send_event(CABIN_TEMPERATURE_EVENTGROUP_ID, CABIN_TEMPERATURE_CHANGED_EVENT_ID, payload)
        logger.info("Published CabinTemperatureChanged: %.1f C | target: %.1f C", current_cabin_temperature_tenths / 10, requested_target_temperature_tenths / 10)
        await asyncio.sleep(3)


async def main() -> None:
    set_someipy_log_level(logging.INFO)
    logger.info("Starting Climate ECU provider")
    daemon = await connect_to_someipy_daemon()
    service_instance = ServerServiceInstance(daemon=daemon, service=build_provider_service(), instance_id=CLIMATE_INSTANCE_ID, endpoint_ip=LOOPBACK_IP, endpoint_port=CLIMATE_PROVIDER_PORT, ttl=5, cyclic_offer_delay_ms=2000)
    await service_instance.start_offer()
    logger.info("ClimateService offered | Service ID=0x%04X | %s:%d", CLIMATE_SERVICE_ID, LOOPBACK_IP, CLIMATE_PROVIDER_PORT)
    publisher_task = asyncio.create_task(publish_temperature_updates(service_instance))
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
        logger.info("Climate ECU stopped cleanly")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nClimate ECU stopped by user.")
