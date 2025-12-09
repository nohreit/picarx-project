#!/usr/bin/env python3
import time
from picarx import Picarx  # from the SunFounder library

px = Picarx()

def get_distance_cm():
    d = px.get_distance()  # PiCar-X wrapper for the ultrasonic sensor
    # Defensive default: if sensor glitches, return something "far"
    if d is None or d <= 0:
        return 999.0
    return float(d)

def main():
    try:
        while True:
            dist = get_distance_cm()
            print(f"Distance: {dist:6.1f} cm")
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nStopping.")
    finally:
        px.stop()  # just in case we ever move later

if __name__ == "__main__":
    main()
