# DriveLink — Multi-ECU SOME/IP Demonstrator

A Python-based automotive communication demonstrator using `someipy==2.1.2`, UDP and Wireshark. This repository contains the implementation, setup instructions, experiment notes and screenshots from a live Ubuntu 24.04 run.

## Project overview

DriveLink models four independent ECU applications:

| ECU | Role | Responsibility |
|---|---|---|
| Vehicle ECU | Provider | Offers vehicle speed and state; publishes speed and overspeed events |
| Instrument Cluster | Consumer | Calls vehicle methods and subscribes to vehicle events |
| Climate ECU | Provider | Offers cabin-temperature methods and publishes temperature changes |
| Central Display | Consumer | Consumes both VehicleSpeedService and ClimateService |

All applications run as separate processes on `127.0.0.1`. This is a software demonstrator and does not connect to physical vehicle hardware.

## Services

### VehicleSpeedService

- Service ID `0x1234`, instance ID `0x5678`, major version 1
- `GetSpeed` method `0x0001`
- `GetVehicleState` method `0x0002` (`0=STOPPED`, `1=MOVING`)
- `SpeedChanged` event `0x8001`, event group `0x0001`
- `OverspeedWarning` event `0x8002`, event group `0x0002`, triggered strictly above 80 km/h
- Provider endpoint `127.0.0.1:3000`

### ClimateService

- Service ID `0x2234`, instance ID `0x0001`, major version 1
- `GetCabinTemperature` method `0x0001`
- `SetTargetTemperature` method `0x0002`; accepts 16.0–30.0 °C inclusive
- `CabinTemperatureChanged` event `0x8001`, event group `0x0001`
- Temperatures are encoded as signed 16-bit tenths of a degree Celsius
- Provider endpoint `127.0.0.1:3001`

## Repository layout

```text
config/       someipyd daemon configuration
src/          four ECU applications and shared interfaces
 tests/       offline logic unit tests
docs/        run guide, presentation guide and experiment log
screenshots/ actual run screenshots
captures/    packet capture evidence (add the .pcapng from Ubuntu)
```

## Setup (Ubuntu)

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip wireshark git
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
sudo ip addr add 224.224.224.245/32 dev lo
```

If the multicast address already exists, do not add it again. Confirm with `ip addr show dev lo`.

## Run Assignment 1

Open three terminals in the repository root. Activate `.venv` in each terminal.

**Terminal 1 — SOME/IP daemon**

```bash
someipyd --config config/someipyd.json
```

**Terminal 2 — Vehicle ECU provider**

```bash
python -m src.vehicle_ecu.server
```

**Terminal 3 — Instrument Cluster consumer**

```bash
python -m src.instrument_cluster.client
```

## Run Assignment 2

Keep the first three processes running and open two more terminals.

**Terminal 4 — Climate ECU provider**

```bash
python -m src.climate_ecu.server
```

**Terminal 5 — Central Display consumer**

```bash
python -m src.central_display.client
```

Central Display consumes both services. The temperature validation demonstration exercises 22.0, 16.0, 30.0, 10.0 and 35.0 °C; expected outcomes are accepted, accepted, accepted, rejected and rejected respectively.

Stop an application with `Ctrl+C` in its terminal.

## Tests

```bash
python -m unittest discover -s tests -v
```

The eight offline unit tests passed in the recorded run. They cover vehicle state, the strict overspeed threshold and inclusive climate temperature limits. Live inter-process communication was also observed during the Ubuntu run; consult `docs/EXPERIMENT_LOG.md` for the exact evidence and limitations.

## Wireshark

Capture on the loopback interface `lo`. A useful display filter is:

```text
udp.port == 30490 || udp.port == 3000 || udp.port == 3001 || udp.port == 3002 || udp.port == 3004 || udp.port == 3006
```

The submitted screenshots show Service Discovery multicast UDP traffic and Climate ECU request/response UDP packets. Wireshark captured 50 packets with zero drops in the recorded capture. The screenshots do not establish successful SOME/IP protocol dissection; the captured frames were displayed as UDP. The actual `assignment2.pcapng` file must be copied from the Ubuntu VM into `captures/` if it is to be included in the repository. No Assignment 1 `.pcapng` was supplied.

## Evidence

See [`screenshots/README.md`](screenshots/README.md) for the screenshot index and [`docs/EXPERIMENT_LOG.md`](docs/EXPERIMENT_LOG.md) for the observed experiments and evidence gaps. The screenshots document the Instrument Cluster, Central Display, Climate ECU, service failure/recovery, and Wireshark inspection.

## References

- [SOME/IP Assignment 1](https://kapexlab.github.io/automotive-communication-networks/assignments/SOMEIP1.html)
- [SOME/IP Assignment 2](https://kapexlab.github.io/automotive-communication-networks/assignments/SOMEIP2.html)
- [someipy v2.1.2 Getting Started](https://someipy.readthedocs.io/en/v2.1.2/getting_started.html)
- [someipy v2.1.2 ServiceBuilder API](https://someipy.readthedocs.io/en/v2.1.2/api/service_builder.html)
- [someipy v2.1.2 ServerServiceInstance API](https://someipy.readthedocs.io/en/v2.1.2/api/server_service_instance.html)
