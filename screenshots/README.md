# DriveLink — Actual Run Evidence

These screenshots are from the user's Ubuntu 24.04 run on 18 November 2026. They show actual terminal and Wireshark output; they are not generated examples.

| File | Evidence |
|---|---|
| `01-<img width="938" height="487" alt="Screenshot 2026-11-18 185402" src="https://github.com/user-attachments/assets/fc44745b-0a1a-45fe-a850-52f92c96993a" />
` | Instrument Cluster discovers VehicleSpeedService, receives speed/state values and warns at 90/100 km/h |
| `02-<img width="655" height="467" alt="Screenshot 2026-11-18 185637" src="https://github.com/user-attachments/assets/21c3b24c-7628-4286-bbe4-1345be7d9aa8" />
` | Central Display sees both services; 22/16/30°C accepted and 10°C rejected (35°C result not visible) |
| `03-<img width="809" height="454" alt="Screenshot 2026-11-18 185623" src="https://github.com/user-attachments/assets/a4edfc65-187c-4010-a8f1-e36aa357602c" />
` | Climate ECU starts with corrected logger and receives GetCabinTemperature requests |
| `04-<img width="655" height="467" alt="Screenshot 2026-11-18 185637" src="https://github.com/user-attachments/assets/95b3aef2-82a8-40aa-aa4d-70584a114e3c" />
` | Central Display receives vehicle speed/overspeed events |
| `05-<img width="951" height="512" alt="Screenshot 2026-11-18 190629" src="https://github.com/user-attachments/assets/d155b1ce-a7d3-402e-98f1-36e7308887d7" />
` | Climate ECU restarted; Central Display temperature requests resume |
| `06-<img width="866" height="481" alt="Screenshot 2026-11-18 191308" src="https://github.com/user-attachments/assets/e08f4d3c-f006-4fcf-b5ea-2383324bdc3a" />
` | VehicleSpeedService DOWN while climate continues |
| `07-<img width="739" height="292" alt="Screenshot 2026-11-18 191354" src="https://github.com/user-attachments/assets/f1918721-8bc0-42f9-85db-066ae2031005" />
` | VehicleSpeedService UP and vehicle updates resume |
| `08-<img width="443" height="290" alt="Screenshot 2026-11-18 192110" src="https://github.com/user-attachments/assets/0921269e-9703-4890-9aca-153a63eebc6a" />
` | 50 packets captured, 0 dropped; loopback UDP and multicast traffic |
| `09-<img width="342" height="236" alt="Screenshot 2026-11-18 192240" src="https://github.com/user-attachments/assets/0ad61c22-e519-48b2-a504-abe7d5ee63cf" />
` | Packet 12: Climate ECU 3001 to Central Display 3006 |
| `10-<img width="326" height="239" alt="Screenshot 2026-11-18 192221" src="https://github.com/user-attachments/assets/a1e1339c-33c5-44e4-8ff0-da5bb6c03e66" />
` | Packet 11: Central Display 3006 to Climate ECU 3001 |


