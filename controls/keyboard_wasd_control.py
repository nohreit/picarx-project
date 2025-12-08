import sys
import termios
import tty
import time

from picarx import Picarx

# ===== Low-level keyboard handling =====

def getch():
    """
    Read a single character from stdin (blocking), without requiring Enter.
    Restores terminal settings afterward.
    """
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)  # read exactly one char
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


# ===== Robot control =====

def main():
    px = Picarx()
    speed = 30             # base speed (0–100)
    steer_angle = 25       # degrees for turning

    print("""
================= PiCar-X WASD Keyboard Control =================

Controls:
  w : forward
  s : backward
  a : turn left (forward with steering)
  d : turn right (forward with steering)

  space : STOP
  q     : quit

Notes:
  - Make sure the car has space to move!
  - Keep it on the floor, not on your desk.
  - Run this script with:  sudo python3 keyboard_wasd_control.py

===============================================================
""")

    try:
        # Ensure robot is in a safe default state
        px.set_dir_servo_angle(0)
        px.stop()

        while True:
            ch = getch()

            if ch == "q":
                print("Quitting...")
                break

            elif ch == " ":
                print("[SPACE] Stop")
                px.stop()

            elif ch == "w":
                print("[W] Forward")
                px.set_dir_servo_angle(0)
                px.forward(speed)

            elif ch == "s":
                print("[S] Backward")
                px.set_dir_servo_angle(0)
                px.backward(speed)

            elif ch == "a":
                print("[A] Turn left (forward)")
                px.set_dir_servo_angle(-steer_angle)
                px.forward(speed)

            elif ch == "d":
                print("[D] Turn right (forward)")
                px.set_dir_servo_angle(steer_angle)
                px.forward(speed)

            else:
                # Ignore other keys, but you could print them for debugging
                # print(f"Unknown key: {repr(ch)}")
                pass

    except KeyboardInterrupt:
        print("\nKeyboardInterrupt – stopping robot.")
    finally:
        print("Stopping motors and resetting steering...")
        px.stop()
        px.set_dir_servo_angle(0)
        px.set_cam_pan_angle(0)
        px.set_cam_tilt_angle(0)
        px.close()


if __name__ == "__main__":
    main()
