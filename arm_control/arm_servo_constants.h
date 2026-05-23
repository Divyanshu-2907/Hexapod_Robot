// 4-DOF arm servo pins and limits — mirror of receiver_v4.0 firmware
// Include in sketches or keep in sync with receiver_v4.0/receiver_v4.0.ino

#ifndef ARM_SERVO_CONSTANTS_H
#define ARM_SERVO_CONSTANTS_H

#define PIN_SHOULDER_L   41
#define PIN_SHOULDER_R   42
#define PIN_ELBOW        43
#define PIN_BASE_ROT     44
#define PIN_WRIST_TILT    7
#define PIN_WRIST_ROT     8
#define PIN_GRIPPER      12

#define MG90S_MIN_US   700
#define MG90S_MAX_US  2300

#define SHOULDER_MIN   30
#define SHOULDER_MAX  150
#define ELBOW_MIN      10
#define ELBOW_MAX     170
#define WRIST_TILT_MIN  0
#define WRIST_TILT_MAX 180
#define WRIST_ROT_MIN   0
#define WRIST_ROT_MAX  180
#define WRIST_ROT_HOME 90
#define BASE_ROT_MIN    0
#define BASE_ROT_MAX  180
#define BASE_ROT_HOME  90
#define GRIPPER_MIN    30
#define GRIPPER_MAX   150

#define SHOULDER_RATE  0.4f
#define ELBOW_RATE     0.5f
#define WRIST_ROT_RATE 0.6f
#define BASE_ROT_RATE  0.5f
#define ARM_SMOOTH     0.06f

#define WAVE_SHOULDER_CENTER  90.0f
#define WAVE_SHOULDER_AMP     35.0f
#define WAVE_ELBOW_CENTER     80.0f
#define WAVE_ELBOW_AMP        30.0f

#define PP_LOWER_SHOULDER   130.0f
#define PP_LOWER_ELBOW      140.0f
#define PP_RAISE_SHOULDER    50.0f
#define PP_RAISE_ELBOW       60.0f
#define PP_SWING_BASE       140.0f

#endif
