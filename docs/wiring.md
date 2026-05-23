# Wiring Reference

## Transmitter (Arduino Uno) — `transmitter_v3.0/`

| Connection | Pin |
|------------|-----|
| NRF24L01 CE | D9 |
| NRF24L01 CSN | D10 |
| Joy1 VRx / VRy | A0 / A1 |
| Joy2 VRx / VRy | A2 / A3 |
| Pot1 / Pot2 | A4 / A5 |
| TG1 / TG2 | D2 / D3 |
| SW1 / SW2 | D4 / D5 |
| TG3 (mode) | D6 |
| TG4 (step height vs length) | D7 |

## Receiver (Arduino Mega 2560) — `receiver_v4.0/`

| Subsystem | Pins |
|-----------|------|
| NRF24 CE / CS | 2 / 3 |
| Leg RF / RM / RR | 28–30 / 25–27 / 22–24 |
| Leg LR / LM / LF | 31–33 / 34–36 / 37–39 |
| Arm shoulders / elbow / base | 41 / 42 / 43 / 44 |
| Wrist tilt / rot / gripper | 7 / 8 / 12 |

**NRF24 pipe:** `0xE8E8F0F0E1`
