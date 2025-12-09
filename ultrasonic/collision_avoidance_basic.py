#!/usr/bin/env python3
import time
from picarx import Picarx

px = Picarx()

SAFE_DIST = 40.0   # cm
DANGER_DIST = 20.0 # cm

FORWARD_SPEED = 10  # small, safe values; adjust later
SLOW_SPEED    = 5

def get_distance_cm():
    d = px.get_distance()
    if d is None or d <= 0:
        return 999.0
    return float(d)

def main():
    print("Starting basic collision avoidance. Ctrl+C to stop.")
    try:
        while True:
            dist = get_distance_cm()
            print(f"Distance: {dist:6.1f} cm", end="\r")

            if dist < DANGER_DIST:
                # Immediate stop & small reverse pulse
                px.stop()
                time.sleep(0.1)
                px.backward(SLOW_SPEED)
                time.sleep(0.3)
                px.stop()
            elif dist < SAFE_DIST:
                # Caution zone: move slowly
                px.forward(SLOW_SPEED)
            else:
                # All clear: normal slow cruising
                px.forward(FORWARD_SPEED)

            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\nStopping.")
    finally:
        px.stop()

if __name__ == "__main__":
    main()
