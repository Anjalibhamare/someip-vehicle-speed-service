# DriveLink Run and Test Guide

## Setup

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip wireshark git
cd someip-vehicle-speed-service
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
sudo ip addr add 224.224.224.245/32 dev lo
```

If the multicast address already exists, do not add it again. Confirm with `ip addr show dev lo`.

## Assignment 1 — three terminals

Terminal 1:

```bash
someipyd --config config/someipyd.json
```

Terminal 2:

```bash
python -m src.vehicle_ecu.server
```

Terminal 3:

```bash
python -m src.instrument_cluster.client
```

Expected: the cluster discovers VehicleSpeedService, calls GetSpeed/GetVehicleState, receives SpeedChanged events and receives OverspeedWarning above 80 km/h.

## Assignment 2 — two additional terminals

Terminal 4:

```bash
python -m src.climate_ecu.server
```

Terminal 5:

```bash
python -m src.central_display.client
```

Expected: Central Display independently discovers VehicleSpeedService and ClimateService, receives vehicle and cabin-temperature updates, and tests the temperature limits. The program's demonstration requests 22.0, 16.0, 30.0, 10.0 and 35.0°C.

## Offline tests

```bash
python -m unittest discover -s tests -v
```

The observed run passed all 8 tests.

## Wireshark

Capture on loopback (`lo`). Display filter:

```text
udp.port == 30490 || udp.port == 3000 || udp.port == 3001 || udp.port == 3002 || udp.port == 3004 || udp.port == 3006
```

The supplied evidence shows 50 packets captured with zero drops; see `screenshots/README.md` and `docs/EXPERIMENT_LOG.md` for limitations.
