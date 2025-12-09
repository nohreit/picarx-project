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
SPEED_STEP = 5
MIN_SPEED = 10
MAX_SPEED = 100

# Camera pan/tilt config
CAM_STEP = 5  # degrees per keypress
CAM_PAN_MAX = 45  # left/right limit
CAM_TILT_MAX = 45  # up/down limit


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
        "Open on another device (same network):\n"
        "  http://<pi-ip>:9000/mjpg\n"
        "  http://<pi-ip>:9000/ui\n"
    )


def main():
    px = Picarx()

    speed = DEFAULT_SPEED
    steering_angle = 0
    motion = "stop"

    cam_pan = 0  # left(-) / right(+)
    cam_tilt = 0  # up(+?) / down(-?) -> depends on hardware, we’ll use:
    # i: tilt up  (increase)
    # k: tilt down (decrease)

    print(
        f"""
================ PiCar-X Teleop =================

Drive:
  w : forward       (keep steering)
  s : backward      (keep steering)
  a : steer LEFT    (no movement)
  d : steer RIGHT   (no movement)

Speed:
  + or = : increase speed
  - or _ : decrease speed
  (current base speed starts at {DEFAULT_SPEED})

Camera Pan/Tilt:
  i : tilt UP
  k : tilt DOWN
  j : pan LEFT
  l : pan RIGHT

Other:
  space : STOP motors (steering & camera angles stay)
  q     : quit

Safety:
  - Auto STOP if ultrasonic < {ULTRASONIC_STOP_CM} cm while moving forward.

Camera stream:
  http://<pi-ip>:9000/ui
=================================================
"""
    )

    start_camera()

    # Put terminal in raw mode
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    tty.setraw(fd)

    try:
        # Initial pose
        px.set_dir_servo_angle(steering_angle)
        px.set_cam_pan_angle(cam_pan)
        px.set_cam_tilt_angle(cam_tilt)
        px.stop()

        while True:
            ch = read_key_nonblocking()

            # ========== KEY HANDLING ==========
            if ch is not None:

                # --- Quit / Stop ---
                if ch == "q":
                    print("\nQuitting...")
                    break

                elif ch == " ":
                    print("[SPACE] STOP")
                    px.stop()
                    motion = "stop"

                # --- Drive ---
                elif ch == "w":
                    print(f"[W] Forward @ {speed}, steering={steering_angle}°")
                    px.set_dir_servo_angle(steering_angle)
                    px.forward(speed)
                    motion = "forward"

                elif ch == "s":
                    print(f"[S] Backward @ {speed}, steering={steering_angle}°")
                    px.set_dir_servo_angle(steering_angle)
                    px.backward(speed)
                    motion = "backward"

                # --- Steering (no motion) ---
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

                # --- Speed control ---
                elif ch in ["+", "="]:
                    speed = clamp(speed + SPEED_STEP, MIN_SPEED, MAX_SPEED)
                    print(f"[+] Speed increased → {speed}")

                elif ch in ["-", "_"]:
                    speed = clamp(speed - SPEED_STEP, MIN_SPEED, MAX_SPEED)
                    print(f"[-] Speed decreased → {speed}")

                # --- Camera pan/tilt ---
                elif ch == "j":  # pan LEFT
                    cam_pan -= CAM_STEP
                    cam_pan = clamp(cam_pan, -CAM_PAN_MAX, CAM_PAN_MAX)
                    px.set_cam_pan_angle(cam_pan)
                    print(f"[J] Camera PAN LEFT → {cam_pan}°")

                elif ch == "l":  # pan RIGHT
                    cam_pan += CAM_STEP
                    cam_pan = clamp(cam_pan, -CAM_PAN_MAX, CAM_PAN_MAX)
                    px.set_cam_pan_angle(cam_pan)
                    print(f"[L] Camera PAN RIGHT → {cam_pan}°")

                elif ch == "i":  # tilt UP
                    cam_tilt += CAM_STEP
                    cam_tilt = clamp(cam_tilt, -CAM_TILT_MAX, CAM_TILT_MAX)
                    px.set_cam_tilt_angle(cam_tilt)
                    print(f"[I] Camera TILT UP → {cam_tilt}°")

                elif ch == "k":  # tilt DOWN
                    cam_tilt -= CAM_STEP
                    cam_tilt = clamp(cam_tilt, -CAM_TILT_MAX, CAM_TILT_MAX)
                    px.set_cam_tilt_angle(cam_tilt)
                    print(f"[K] Camera TILT DOWN → {cam_tilt}°")

            # ========== ULTRASONIC SAFETY ==========
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

        print("\nResetting steering and camera, stopping motors...")
        try:
            px.stop()
            px.set_dir_servo_angle(0)
            px.set_cam_pan_angle(0)
            px.set_cam_tilt_angle(0)
            px.close()
        except Exception:
            pass


if __name__ == "__main__":
    main()
