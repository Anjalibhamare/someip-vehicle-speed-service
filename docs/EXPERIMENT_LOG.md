# Experiment Log — DriveLink SOME/IP

## Environment

- Observed run: 18 November 2026
- OS: Ubuntu 24.04
- Python: 3.12
- someipy: 2.1.2
- Interface: loopback `lo`; multicast group `224.224.224.245`
- Local endpoints: `127.0.0.1`

## Offline tests

- `python -m unittest discover -s tests -v`: 8 tests passed.
- `python -m py_compile src/climate_ecu/server.py`: completed without output after correcting the Climate ECU log formatting/indentation.

## Assignment 1 — Vehicle speed service

| Test | Observed result | Status |
|---|---|---|
| Vehicle provider | VehicleSpeedService ID `0x1234` offered at `127.0.0.1:3000` | Pass |
| Instrument Cluster discovery | Cluster reported service AVAILABLE | Pass |
| GetSpeed/GetVehicleState | Speed and MOVING/STOPPED values displayed | Pass |
| SpeedChanged | Periodic changing speed events received | Pass |
| OverspeedWarning | Warning at 90 and 100 km/h; none at exactly 80 km/h | Pass |
| Assignment 1 pcapng | No separate capture supplied | Not captured |

## Assignment 2 — Multi-ECU network

| Test | Observed result | Status |
|---|---|---|
| Climate provider | ClimateService ID `0x2234` at `127.0.0.1:3001` | Pass |
| Central Display discovers both services | VehicleSpeedService and ClimateService shown UP/AVAILABLE | Pass |
| Multiple consumers | Instrument Cluster and Central Display consume VehicleSpeedService | Pass |
| Multi-service consumer | Central Display consumes vehicle and climate services | Pass |
| GetCabinTemperature | Climate ECU logged requests from Central Display endpoint `127.0.0.1:3006` | Pass |
| SetTargetTemperature | 22.0, 16.0 and 30.0°C accepted; 10.0°C rejected; 35.0°C rejection not visible in supplied screenshot | Partial evidence |
| CabinTemperatureChanged | Climate provider published updates; Central Display received updates | Pass |
| Vehicle provider failure | Central Display reported VehicleSpeedService DOWN while climate updates continued | Pass |
| Vehicle provider recovery | Central Display reported VehicleSpeedService UP and speed events resumed | Pass |
| Climate restart | Climate provider restarted and subsequent requests resumed; explicit Central Display DOWN/UP transition not captured | Partial evidence |
| Wireshark capture | 50 packets, 0 drops on `lo`; UDP 30490 multicast and UDP 3006→3001 / 3001→3006 observed | Packet capture pass; SOME/IP dissection not verified |

## Problems fixed

- Climate ECU logging format had three placeholders but initially only two values. The log call now includes `LOOPBACK_IP` and `CLIMATE_PROVIDER_PORT`.
- A duplicate/mis-indented logger block caused `IndentationError`; it was replaced with one correctly indented block and checked using `py_compile`.
- Wireshark GUI did not expose `lo` in the welcome capture list; `sudo dumpcap -D` confirmed loopback and capture was started with `sudo dumpcap -i lo`.
- Capture file permissions required copying from `/tmp` with `sudo cp` and changing ownership.

## Evidence limitations / remaining artifacts

- The actual `assignment2.pcapng` file was created on the Ubuntu VM but was not transferred into this repository upload. Add the raw file under `captures/` if required.
- No Assignment 1 pcapng was supplied.
- Wireshark screenshots show UDP frames and endpoint directions. The protocol column remained UDP/DIS; successful SOME/IP protocol-tree dissection was not confirmed.
- The supplied screenshot set does not show the 35.0°C rejection or an explicit ClimateService DOWN/UP transition.
