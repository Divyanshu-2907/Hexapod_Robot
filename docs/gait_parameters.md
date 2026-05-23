# Gait Parameters (Receiver v4.0)

Tunable constants in `receiver_v4.0/receiver_v4.0.ino`:

| Parameter | Purpose |
|-----------|---------|
| `WALK_SMOOTH_XY` / `WALK_SMOOTH_Z` | Foot target smoothing during walk |
| `T_INC_MIN` / `T_INC_MAX` | Gait phase speed range |
| `PATROL_FORWARD_CYCLES` / `PATROL_TURN_CYCLES` | Auto-patrol behavior |
| `PATROL_WALK_SPEED` / `PATROL_STEP_HEIGHT` | Patrol motion profile |
| `DEMO_CYCLE_STEPS` | Demo wave gait length |
| `COXA_LENGTH` / `FEMUR_LENGTH` / `TIBIA_LENGTH` | Leg IK geometry (mm) |
| `SIT_Z` / `STAND_Z` | Body height for sit/stand (mm) |

Live tuning via transmitter (hexapod mode): Pot1 = walk speed, Pot2 = step height, Joy2-Y = body height, TG4 toggles step length on Pot2.
