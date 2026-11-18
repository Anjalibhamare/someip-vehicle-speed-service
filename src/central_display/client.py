"""Central Display ECU: consumes VehicleSpeedService and ClimateService."""
import asyncio
import logging
from someipy import ClientServiceInstance, MessageType, ReturnCode, connect_to_someipy_daemon
from someipy.someipy_logging import set_someipy_log_level
from src.common.vehicle_interface import CENTRAL_VEHICLE_CLIENT_PORT, GET_SPEED_METHOD_ID, GET_VEHICLE_STATE_METHOD_ID, LOOPBACK_IP, OVERSPEED_WARNING_EVENT_ID, SPEED_CHANGED_EVENT_ID, VEHICLE_INSTANCE_ID, SpeedPayload, VehicleStatePayload, overspeed_eventgroup, speed_eventgroup, vehicle_service
from src.common.climate_interface import CABIN_TEMPERATURE_CHANGED_EVENT_ID, CENTRAL_CLIMATE_CLIENT_PORT, CLIMATE_INSTANCE_ID, GET_CABIN_TEMPERATURE_METHOD_ID, SET_TARGET_TEMPERATURE_METHOD_ID, TARGET_ACCEPTED, CabinTemperaturePayload, TargetTemperaturePayload, TargetTemperatureStatusPayload, cabin_temperature_eventgroup, climate_service

logging.basicConfig(level=logging.INFO, format="%(asctime)s | CENTRAL-DISPLAY | %(levelname)s | %(message)s")
logger = logging.getLogger("central_display")


def on_vehicle_event(event_id: int, payload: bytes) -> None:
    try:
        speed = SpeedPayload().deserialize(payload).speed_kmph.value
        if event_id == SPEED_CHANGED_EVENT_ID:
            print(f"[DISPLAY / VEHICLE] Speed update: {speed} km/h")
        elif event_id == OVERSPEED_WARNING_EVENT_ID:
            print(f"[DISPLAY / SAFETY] *** OVERSPEED WARNING: {speed} km/h ***")
    except Exception:
        logger.exception("Could not decode a vehicle event")


def on_climate_event(event_id: int, payload: bytes) -> None:
    try:
        if event_id == CABIN_TEMPERATURE_CHANGED_EVENT_ID:
            value = CabinTemperaturePayload().deserialize(payload).temperature_tenths_c.value
            print(f"[DISPLAY / CLIMATE] Cabin temperature update: {value / 10:.1f} C")
    except Exception:
        logger.exception("Could not decode a climate event")


async def read_vehicle_data(client: ClientServiceInstance) -> None:
    while True:
        try:
            if not await client.is_available():
                await asyncio.sleep(1)
                continue
            speed_response = await client.call_method(GET_SPEED_METHOD_ID, b"")
            state_response = await client.call_method(GET_VEHICLE_STATE_METHOD_ID, b"")
            if speed_response.message_type == MessageType.RESPONSE and speed_response.return_code == ReturnCode.E_OK and state_response.message_type == MessageType.RESPONSE and state_response.return_code == ReturnCode.E_OK:
                speed = SpeedPayload().deserialize(speed_response.payload).speed_kmph.value
                state = VehicleStatePayload().deserialize(state_response.payload).state.value
                print(f"[DISPLAY / VEHICLE] Snapshot: {speed} km/h | {'STOPPED' if state == 0 else 'MOVING'}")
            else:
                print("[DISPLAY / VEHICLE] One of the vehicle methods returned an error")
        except Exception as error:
            logger.warning("Vehicle service request failed; retrying: %s", error)
        await asyncio.sleep(5)


async def read_climate_data(client: ClientServiceInstance) -> None:
    while True:
        try:
            if not await client.is_available():
                await asyncio.sleep(1)
                continue
            response = await client.call_method(GET_CABIN_TEMPERATURE_METHOD_ID, b"")
            if response.message_type == MessageType.RESPONSE and response.return_code == ReturnCode.E_OK:
                value = CabinTemperaturePayload().deserialize(response.payload).temperature_tenths_c.value
                print(f"[DISPLAY / CLIMATE] GetCabinTemperature: {value / 10:.1f} C")
            else:
                print("[DISPLAY / CLIMATE] GetCabinTemperature returned an error")
        except Exception as error:
            logger.warning("Climate service request failed; retrying: %s", error)
        await asyncio.sleep(5)


async def monitor_service_health(vehicle_client: ClientServiceInstance, climate_client: ClientServiceInstance) -> None:
    previous = {"VehicleSpeedService": None, "ClimateService": None}
    while True:
        current = {"VehicleSpeedService": await vehicle_client.is_available(), "ClimateService": await climate_client.is_available()}
        for service_name, available in current.items():
            if previous[service_name] is None or previous[service_name] != available:
                status = "UP / AVAILABLE" if available else "DOWN / UNAVAILABLE"
                print(f"[DISPLAY / SERVICE-HEALTH] {service_name}: {status}")
                if available:
                    if service_name == "VehicleSpeedService":
                        vehicle_client.subscribe_eventgroup(speed_eventgroup, 5)
                        vehicle_client.subscribe_eventgroup(overspeed_eventgroup, 5)
                        print("[DISPLAY] Vehicle event groups subscribed")
                    else:
                        climate_client.subscribe_eventgroup(cabin_temperature_eventgroup, 5)
                        print("[DISPLAY] Climate event group subscribed")
                previous[service_name] = available
        await asyncio.sleep(1)


async def run_temperature_validation_when_ready(client: ClientServiceInstance) -> None:
    while not await client.is_available():
        await asyncio.sleep(1)
    await run_temperature_validation(client)


async def run_temperature_validation(client: ClientServiceInstance) -> None:
    print("\n[DISPLAY] Temperature validation demonstration")
    print("[DISPLAY] Allowed range: 16.0 C to 30.0 C (inclusive)")
    for requested in (220, 160, 300, 100, 350):
        response = await client.call_method(SET_TARGET_TEMPERATURE_METHOD_ID, TargetTemperaturePayload(requested).serialize())
        if response.message_type == MessageType.RESPONSE and response.return_code == ReturnCode.E_OK:
            status = TargetTemperatureStatusPayload().deserialize(response.payload).status.value
            result_text = "ACCEPTED" if status == TARGET_ACCEPTED else "REJECTED (outside allowed range)"
        else:
            result_text = "SOME/IP METHOD ERROR"
        print(f"[DISPLAY] SetTargetTemperature({requested / 10:.1f} C) -> {result_text}")
        await asyncio.sleep(1)


async def main() -> None:
    set_someipy_log_level(logging.INFO)
    print("=" * 66)
    print("DRIVELINK | CENTRAL DISPLAY ECU")
    print("Role: consumer of VehicleSpeedService + ClimateService")
    print("=" * 66)
    daemon = await connect_to_someipy_daemon()
    vehicle_client = ClientServiceInstance(daemon=daemon, service=vehicle_service, instance_id=VEHICLE_INSTANCE_ID, endpoint_ip=LOOPBACK_IP, endpoint_port=CENTRAL_VEHICLE_CLIENT_PORT)
    climate_client = ClientServiceInstance(daemon=daemon, service=climate_service, instance_id=CLIMATE_INSTANCE_ID, endpoint_ip=LOOPBACK_IP, endpoint_port=CENTRAL_CLIMATE_CLIENT_PORT)
    vehicle_client.register_callback(on_vehicle_event)
    climate_client.register_callback(on_climate_event)
    tasks = []
    try:
        tasks = [asyncio.create_task(read_vehicle_data(vehicle_client)), asyncio.create_task(read_climate_data(climate_client)), asyncio.create_task(monitor_service_health(vehicle_client, climate_client)), asyncio.create_task(run_temperature_validation_when_ready(climate_client))]
        print("\n[DISPLAY] Independent service discovery is active.")
        print("[DISPLAY] Start Vehicle ECU and Climate ECU in either order.")
        print("[DISPLAY] Live monitoring active. Press Ctrl+C to stop.\n")
        await asyncio.Future()
    finally:
        for task in tasks:
            task.cancel()
        for task in tasks:
            try:
                await task
            except asyncio.CancelledError:
                pass
        await daemon.disconnect_from_daemon()
        logger.info("Central Display disconnected")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nCentral Display stopped by user.")
