#!/usr/bin/env python3
# Finite State Machine based collision avoidance for PiCar-X using ultrasonic sensor (reflex agent)
import time
from enum import Enum
from picarx import Picarx

px = Picarx()

class Zone(Enum):
    SAFE = 0
    CAUTION = 1
    DANGER = 2

SAFE_DIST    = 50.0  # cm
CAUTION_DIST = 30.0  # cm

FAST_SPEED = 15
SLOW_SPEED = 8
TURN_SPEED = 10

def get_distance_cm():
    d = px.get_distance()
    if d is None or d <= 0:
        return 999.0
    return float(d)

def classify_zone(dist: float) -> Zone:
    if dist < CAUTION_DIST:
        return Zone.DANGER
    elif dist < SAFE_DIST:
        return Zone.CAUTION
    else:
        return Zone.SAFE

def main():
    print("Starting FSM-based collision avoidance. Ctrl+C to stop.")
    state = Zone.SAFE

    try:
        while True:
            dist = get_distance_cm()
            state = classify_zone(dist)
            print(f"Dist: {dist:6.1f} cm | State: {state.name:7}", end="\r")

            if state == Zone.SAFE:
                # Drive forward at normal speed
                px.forward(FAST_SPEED)

            elif state == Zone.CAUTION:
                # Slow down and maybe veer a bit
                px.forward(SLOW_SPEED)
                # Tiny steering bias to the left to "search" for free space
                px.set_dir_servo_angle(-10)

            elif state == Zone.DANGER:
                # Stop and execute an evasive maneuver
                px.stop()
                time.sleep(0.1)

                # Back up a bit
                px.backward(SLOW_SPEED)
                time.sleep(0.4)
                px.stop()

                # Turn in place a bit to find a new heading
                px.set_dir_servo_angle(30)  # right turn
                px.forward(TURN_SPEED)
                time.sleep(0.4)
                px.stop()
                # Center steering again
                px.set_dir_servo_angle(0)

            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\nStopping.")
    finally:
        px.stop()
        px.set_dir_servo_angle(0)

if __name__ == "__main__":
    main()
