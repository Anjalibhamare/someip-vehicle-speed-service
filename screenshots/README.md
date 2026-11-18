# DriveLink — Actual Run Evidence

These screenshots are from the user's Ubuntu 24.04 run on 18 November 2026. They show actual terminal and Wireshark output; they are not generated examples.

| File | Evidence |
|---|---|
| `01-instrument-cluster-overspeed.png` | Instrument Cluster discovers VehicleSpeedService, receives speed/state values and warns at 90/100 km/h |
| `02-central-display-temperature-validation.png` | Central Display sees both services; 22/16/30°C accepted and 10°C rejected (35°C result not visible) |
| `03-climate-ecu-fixed-and-communicating.png` | Climate ECU starts with corrected logger and receives GetCabinTemperature requests |
| `04-central-display-vehicle-events.png` | Central Display receives vehicle speed/overspeed events |
| `05-climate-ecu-after-restart.png` | Climate ECU restarted; Central Display temperature requests resume |
| `06-vehicle-service-failure-climate-continues.png` | VehicleSpeedService DOWN while climate continues |
| `07-vehicle-service-recovery.png` | VehicleSpeedService UP and vehicle updates resume |
| `08-wireshark-50-packet-capture.png` | 50 packets captured, 0 dropped; loopback UDP and multicast traffic |
| `09-wireshark-climate-response-packet.png` | Packet 12: Climate ECU 3001 to Central Display 3006 |
| `10-wireshark-climate-request-packet.png` | Packet 11: Central Display 3006 to Climate ECU 3001 |

## Limitations

- The actual `assignment2.pcapng` was created in Ubuntu but was not included in the supplied evidence bundle; copy it into `captures/` if required.
- No Assignment 1 pcapng was supplied.
- Wireshark showed these frames as UDP, not a verified SOME/IP decode. Describe them as UDP endpoint/SD traffic evidence, not a decoded SOME/IP protocol tree.
- The screenshot set does not show the 35°C rejection or explicit ClimateService DOWN/UP display transition.
