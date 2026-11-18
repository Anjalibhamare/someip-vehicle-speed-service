"""Instrument Cluster ECU: SOME/IP consumer of VehicleSpeedService.
Run: python -m src.instrument_cluster.client
"""
import asyncio
import logging
from someipy import ClientServiceInstance, MessageType, ReturnCode, connect_to_someipy_daemon
from someipy.someipy_logging import set_someipy_log_level
from src.common.vehicle_interface import CLUSTER_CLIENT_PORT, GET_SPEED_METHOD_ID, GET_VEHICLE_STATE_METHOD_ID, LOOPBACK_IP, OVERSPEED_WARNING_EVENT_ID, SPEED_CHANGED_EVENT_ID, VEHICLE_INSTANCE_ID, VEHICLE_SERVICE_ID, SpeedPayload, VehicleStatePayload, overspeed_eventgroup, speed_eventgroup, vehicle_service

logging.basicConfig(level=logging.INFO, format="%(asctime)s | INSTRUMENT-CLUSTER | %(levelname)s | %(message)s")
logger = logging.getLogger("instrument_cluster")


def on_vehicle_event(event_id: int, event_payload: bytes) -> None:
    try:
        if event_id == SPEED_CHANGED_EVENT_ID:
            speed = SpeedPayload().deserialize(event_payload).speed_kmph.value
            print(f"\n[CLUSTER] SpeedChanged event  -> {speed} km/h")
        elif event_id == OVERSPEED_WARNING_EVENT_ID:
            speed = SpeedPayload().deserialize(event_payload).speed_kmph.value
            print("\n" + "!" * 58)
            print(f"[CLUSTER] OVERSPEED WARNING  -> {speed} km/h (limit: 80 km/h)")
            print("!" * 58)
        else:
            logger.warning("Received an unrecognised event ID: 0x%04X", event_id)
    except Exception:
        logger.exception("Could not decode a VehicleSpeedService event")


async def wait_for_vehicle_service(client: ClientServiceInstance) -> None:
    print("[CLUSTER] Searching for VehicleSpeedService through Service Discovery...")
    while not await client.is_available():
        print("[CLUSTER] Service not available yet; retrying in 1 second...")
        await asyncio.sleep(1)
    print(f"[CLUSTER] VehicleSpeedService AVAILABLE (ID 0x{VEHICLE_SERVICE_ID:04X})")


async def poll_vehicle_methods(client: ClientServiceInstance) -> None:
    while True:
        try:
            speed_result = await client.call_method(GET_SPEED_METHOD_ID, b"")
            if speed_result.message_type == MessageType.RESPONSE and speed_result.return_code == ReturnCode.E_OK:
                speed = SpeedPayload().deserialize(speed_result.payload).speed_kmph.value
                state_result = await client.call_method(GET_VEHICLE_STATE_METHOD_ID, b"")
                if state_result.message_type == MessageType.RESPONSE and state_result.return_code == ReturnCode.E_OK:
                    state_code = VehicleStatePayload().deserialize(state_result.payload).state.value
                    state_label = "STOPPED" if state_code == 0 else "MOVING"
                    print(f"[CLUSTER] GetSpeed={speed:3d} km/h | GetVehicleState={state_label}")
                else:
                    print("[CLUSTER] GetVehicleState returned a non-success response")
            else:
                print("[CLUSTER] GetSpeed returned a non-success response")
        except Exception as error:
            logger.warning("Vehicle method call failed (will retry): %s", error)
        await asyncio.sleep(5)


async def main() -> None:
    set_someipy_log_level(logging.INFO)
    print("=" * 62)
    print("DRIVELINK | INSTRUMENT CLUSTER ECU")
    print("Role: consumer of VehicleSpeedService")
    print("=" * 62)
    daemon = await connect_to_someipy_daemon()
    client = ClientServiceInstance(daemon=daemon, service=vehicle_service, instance_id=VEHICLE_INSTANCE_ID, endpoint_ip=LOOPBACK_IP, endpoint_port=CLUSTER_CLIENT_PORT)
    client.register_callback(on_vehicle_event)
    poll_task = None
    try:
        await wait_for_vehicle_service(client)
        client.subscribe_eventgroup(speed_eventgroup, 5)
        client.subscribe_eventgroup(overspeed_eventgroup, 5)
        print("[CLUSTER] Subscribed to SpeedChanged and OverspeedWarning")
        poll_task = asyncio.create_task(poll_vehicle_methods(client))
        await asyncio.Future()
    finally:
        if poll_task is not None:
            poll_task.cancel()
            try:
                await poll_task
            except asyncio.CancelledError:
                pass
        await daemon.disconnect_from_daemon()
        logger.info("Instrument Cluster disconnected")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nInstrument Cluster stopped by user.")
