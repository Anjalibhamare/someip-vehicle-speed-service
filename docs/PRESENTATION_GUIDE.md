# DriveLink Presentation Guide

## Suggested explanation

DriveLink is a software demonstrator of service-oriented automotive communication using SOME/IP. Four independent Python applications represent Vehicle ECU, Instrument Cluster, Climate ECU and Central Display. All run as separate processes on one Ubuntu VM using loopback UDP endpoints.

## Architecture

- Vehicle ECU provides VehicleSpeedService (`0x1234`).
- Instrument Cluster and Central Display consume VehicleSpeedService.
- Climate ECU provides ClimateService (`0x2234`).
- Central Display also consumes ClimateService, demonstrating one consumer using multiple services.
- someipyd supports SOME/IP communication and Service Discovery.

## Demo order

1. Start the someipy daemon.
2. Start Vehicle ECU and show its service offer and periodic speed events.
3. Start Instrument Cluster and show service discovery, GetSpeed/GetVehicleState, SpeedChanged and overspeed warnings above 80 km/h.
4. Start Climate ECU and show ClimateService offer and temperature events.
5. Start Central Display and show both services available, vehicle/climate data and target-temperature checks.
6. Stop Vehicle ECU and show VehicleSpeedService DOWN while climate updates continue; restart it and show UP/recovery.
7. Stop/restart Climate ECU if time permits; provider-side request logs after restart are available in the evidence, but explicit Central Display DOWN/UP output was not captured.
8. Show Wireshark traffic and explain what the capture actually demonstrates.

## Key concepts for viva

| Concept | Explanation | Example in DriveLink |
|---|---|---|
| Service ID | Identifies a service | `0x1234`, `0x2234` |
| Method | Request/response operation | GetSpeed, GetCabinTemperature |
| Event | Provider publishes updates | SpeedChanged, CabinTemperatureChanged |
| Event group | Events a consumer subscribes to | Speed and climate event groups |
| Service Discovery | Provider offers and consumer finds services | someipyd and the ECU clients |
| Multi-consumer | Multiple clients use one service | Instrument Cluster + Central Display use VehicleSpeedService |
| Multi-service consumer | One client uses several services | Central Display uses vehicle + climate |

## Useful Q&A

**What is SOME/IP?** Scalable service-Oriented MiddlewarE over IP, used for service-based communication between automotive ECUs.

**Method vs event?** A method is request/response; an event is provider-to-consumer publish/subscribe notification.

**Why separate ECU processes?** It makes providers and consumers independently runnable and allows service failure/recovery experiments.

**How is overspeed detected?** The application emits the warning only when speed is strictly greater than 80 km/h.

**Why encode temperature in tenths?** It represents one decimal place using a small integer; e.g. 24.5°C is sent as 245.

**Are these physical ECUs?** No. They are independent software processes simulating ECU roles on one host.

## Be precise about evidence

The run passed 8 offline unit tests and demonstrated live ECU communication. Wireshark captured 50 packets with zero drops and shows UDP traffic on the loopback interface, including traffic between Central Display and Climate ECU. The provided Wireshark screenshots do not show a decoded SOME/IP protocol tree, so describe them as UDP packet/endpoint evidence rather than claiming successful SOME/IP dissection. See `docs/EXPERIMENT_LOG.md` for other evidence gaps.
