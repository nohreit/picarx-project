import sys
import termios
import tty
import time
import select

from picarx import Picarx
from vilib import Vilib  # Camera

# ===== Config =====
ULTRASONIC_STOP_CM = 20.0
SLEEP_DT = 0.05

STEER_STEP = 8  # degrees per A/D press
MAX_STEER = 35
DEFAULT_SPEED = 30
SPEED_STEP = 5  # speed change per + or -

MIN_SPEED = 10
MAX_SPEED = 100


def read_key_nonblocking(timeout=SLEEP_DT):
    fd = sys.stdin.fileno()
    rlist, _, _ = select.select([fd], [], [], timeout)
    if rlist:
        return sys.stdin.read(1)
    return None


def clamp(x, lo, hi):
    return max(lo, min(hi, x))


def start_camera():
    """Start Vilib camera HTTP stream."""
    Vilib.camera_start(vflip=False, hflip=False)
    Vilib.display(local=False, web=True)
    print(
        "Camera streaming.\n"
        "Open on another device:\n"
        "  http://<pi-ip>:9000/mjpg\n"
        "  http://<pi-ip>:9000/ui\n"
    )


def main():
    px = Picarx()

    speed = DEFAULT_SPEED
    steering_angle = 0
    motion = "stop"

    print(
        f"""
================ PiCar-X Teleop: Camera + WASD + Speed Control ================

Controls:
  w : forward  (keeps steering)
  s : backward (keeps steering)
  a : steer left   (no movement)
  d : steer right  (no movement)

  + or = : increase speed
  - or _ : decrease speed

  space : STOP
  q     : quit

Current starting speed: {DEFAULT_SPEED}

Safety:
  - Auto STOP if ultrasonic < {ULTRASONIC_STOP_CM} cm.

Camera stream available at:
  http://<pi-ip>:9000/ui
===============================================================================
"""
    )

    start_camera()

    # Put terminal in raw mode
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    tty.setraw(fd)

    try:
        px.set_dir_servo_angle(steering_angle)
        px.stop()

        while True:
            ch = read_key_nonblocking()

            # ======== KEY HANDLING =========
            if ch is not None:

                if ch == "q":
                    print("\nQuitting...")
                    break

                elif ch == " ":
                    print("[SPACE] STOP")
                    px.stop()
                    motion = "stop"

                elif ch == "w":
                    print(f"[W] Forward @ speed {speed}, steering={steering_angle}°")
                    px.set_dir_servo_angle(steering_angle)
                    px.forward(speed)
                    motion = "forward"

                elif ch == "s":
                    print(f"[S] Backward @ speed {speed}, steering={steering_angle}°")
                    px.set_dir_servo_angle(steering_angle)
                    px.backward(speed)
                    motion = "backward"

                elif ch == "a":
                    steering_angle -= STEER_STEP
                    steering_angle = clamp(steering_angle, -MAX_STEER, MAX_STEER)
                    px.set_dir_servo_angle(steering_angle)
                    print(f"[A] Steering LEFT → {steering_angle}°")

                elif ch == "d":
                    steering_angle += STEER_STEP
                    steering_angle = clamp(steering_angle, -MAX_STEER, MAX_STEER)
                    px.set_dir_servo_angle(steering_angle)
                    print(f"[D] Steering RIGHT → {steering_angle}°")

                # ======== SPEED CONTROL ========
                elif ch in ["+", "="]:
                    speed = clamp(speed + SPEED_STEP, MIN_SPEED, MAX_SPEED)
                    print(f"[+] Speed increased → {speed}")

                elif ch in ["-", "_"]:
                    speed = clamp(speed - SPEED_STEP, MIN_SPEED, MAX_SPEED)
                    print(f"[-] Speed decreased → {speed}")

            # ======== ULTRASONIC SAFETY =========
            try:
                dist = px.get_distance()
            except Exception:
                dist = -1

            if motion == "forward" and dist > 0 and dist < ULTRASONIC_STOP_CM:
                px.stop()
                motion = "stop"
                print(f"\r[SAFETY] Obstacle at {dist:.1f} cm → STOPPED.", end="")

            time.sleep(SLEEP_DT)

    except KeyboardInterrupt:
        print("\nInterrupted; stopping.")
    finally:
        # Restore terminal
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

        print("\nResetting steering and motors...")
        try:
            px.stop()
            px.set_dir_servo_angle(0)
            px.set_cam_pan_angle(0)
            px.set_cam_tilt_angle(0)
            px.close()
        except:
            pass


if __name__ == "__main__":
    main()
