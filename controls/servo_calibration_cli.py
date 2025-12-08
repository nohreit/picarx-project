from picarx import Picarx
import time


def main():
    px = Picarx()

    # Use the existing calibration values from the object
    current = {
        "dir": px.dir_cali_val,
        "pan": px.cam_pan_cali_val,
        "tilt": px.cam_tilt_cali_val,
    }

    # Start by selecting direction servo
    selected = "dir"
    step = 1  # degrees per adjustment

    help_text = """
================= PiCar-X Servo Calibration =================
Controls:
  [1]  Select DIRECTION servo (front wheels)
  [2]  Select CAMERA PAN servo (left/right)
  [3]  Select CAMERA TILT servo (up/down)

  [a]  Decrease angle by step
  [d]  Increase angle by step

  [s]  Change step size (1 / 2 / 5 / 10)

  [c]  Re-center logical angles to 0 using current calibration
        - After calibration, calling set_*_angle(0) should look "straight"

  [h]  Show this help again
  [q]  Quit

Current servo angle is the *calibration offset* in degrees.
Changes are written to /opt/picar-x/picar-x.conf as you adjust.
=============================================================
"""

    print(help_text)

    def show_status():
        print(f"\nSelected servo : {selected.upper()}")
        print(
            f"Current values : dir={current['dir']}°, pan={current['pan']}°, tilt={current['tilt']}°"
        )
        print(f"Step           : {step}°")

    def apply_calibration():
        # Apply calibration to the selected servo
        if selected == "dir":
            px.dir_servo_calibrate(current["dir"])
        elif selected == "pan":
            px.cam_pan_servo_calibrate(current["pan"])
        elif selected == "tilt":
            px.cam_tilt_servo_calibrate(current["tilt"])

    show_status()

    try:
        while True:
            cmd = input("\nCommand ([h]elp): ").strip().lower()

            if not cmd:
                continue

            if cmd == "q":
                print("Exiting and resetting servos to logical 0°...")
                px.reset()
                break

            elif cmd == "h":
                print(help_text)
                show_status()
                continue

            elif cmd == "1":
                selected = "dir"
                print("Selected DIRECTION servo (front wheels).")
                apply_calibration()
                show_status()
                continue

            elif cmd == "2":
                selected = "pan"
                print("Selected CAMERA PAN servo (left/right).")
                apply_calibration()
                show_status()
                continue

            elif cmd == "3":
                selected = "tilt"
                print("Selected CAMERA TILT servo (up/down).")
                apply_calibration()
                show_status()
                continue

            elif cmd == "a":
                current[selected] -= step
                print(f"{selected} -> {current[selected]}°")
                apply_calibration()
                continue

            elif cmd == "d":
                current[selected] += step
                print(f"{selected} -> {current[selected]}°")
                apply_calibration()
                continue

            elif cmd == "s":
                try:
                    new_step = int(input("New step size (1 / 2 / 5 / 10): ").strip())
                    if new_step in (1, 2, 5, 10):
                        step = new_step
                        print(f"Step size set to {step}°.")
                    else:
                        print("Invalid step size, keeping previous.")
                except ValueError:
                    print("Invalid input, keeping previous step.")
                continue

            elif cmd == "c":
                print("Re-centering logical angles to 0° using current calibration...")
                # After this, px.set_*_angle(0) corresponds to your visually "centered" position
                px.set_dir_servo_angle(0)
                px.set_cam_pan_angle(0)
                px.set_cam_tilt_angle(0)
                show_status()
                continue

            else:
                print("Unknown command. Press [h] for help.")
                continue

    finally:
        # Make sure we leave the robot in a safe state
        print("Stopping motors and resetting servos...")
        px.reset()
        px.close()


if __name__ == "__main__":
    main()
