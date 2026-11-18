# DriveLink — Actual Run Evidence

These screenshots are from the user's Ubuntu 24.04 run on 18 November 2026. They show actual terminal and Wireshark output; they are not generated examples.

| File | Evidence |
|---|---|
| `01-instrument-cluster-overspeed.png` | Instrument Cluster discovers VehicleSpeedService, receives speed/state values and warns at 90/100 km/h |
| `02-central-display-temperature-validation.png` | Central Display sees both services; 22/16/30°C accepted and 10°C rejected (35°C result not visible) |
| `03-<img width="809" height="454" alt="Screenshot 2026-11-18 185623" src="https://github.com/user-attachments/assets/a4edfc65-187c-4010-a8f1-e36aa357602c" />
` | Climate ECU starts with corrected logger and receives GetCabinTemperature requests |
| `04-central-display-vehicle-events.png` | Central Display receives vehicle speed/overspeed events |
| `05-climate-ecu-after-restart.png` | Climate ECU restarted; Central Display temperature requests resume |
| `06-vehicle-service-failure-climate-continues.png` | VehicleSpeedService DOWN while climate continues |
| `07-vehicle-service-recovery.png` | VehicleSpeedService UP and vehicle updates resume |
| `08-wireshark-50-packet-capture.png` | 50 packets captured, 0 dropped; loopback UDP and multicast traffic |
| `09-wireshark-climate-response-packet.png` | Packet 12: Climate ECU 3001 to Central Display 3006 |
| `10-wireshark-climate-request-packet.png` | Packet 11: Central Display 3006 to Climate ECU 3001 |


