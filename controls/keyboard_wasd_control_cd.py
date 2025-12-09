import sys
import termios
import tty
import time
import select

from picarx import Picarx

# ===== Config =====
ULTRASONIC_STOP_CM = 20.0
SLEEP_DT = 0.05

STEER_STEP = 8        # degrees per A/D press
MAX_STEER = 35        # maximum left/right steering angle
DEFAULT_SPEED = 30    # forward/backward speed


def read_key_nonblocking(timeout=SLEEP_DT):
    fd = sys.stdin.fileno()
    rlist, _, _ = select.select([fd], [], [], timeout)
    if rlist:
        return sys.stdin.read(1)
    return None


def clamp(x, lo, hi):
    return max(lo, min(hi, x))


def main():
    px = Picarx()

    speed = DEFAULT_SPEED
    steering_angle = 0       # persistent steering angle
    motion = "stop"          # 'stop', 'forward', 'backward'

    print("""
================= PiCar-X WASD Keyboard Control (Steering Hold) =================

Controls:
  w : move forward (KEEP current steering angle)
  s : move backward (KEEP current steering angle)
  a : steer LEFT   (change angle only, do NOT move)
  d : steer RIGHT  (change angle only, do NOT move)

  space : STOP (motor only, steering angle stays)
  q     : quit

Safety:
  - Automatically STOP if ultrasonic < 20 cm while moving forward.

===============================================================================
""")

    # Put terminal in raw mode
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    tty.setraw(fd)

    try:
        # Initialize safe state
        px.set_dir_servo_angle(steering_angle)
        px.stop()

        while True:
            ch = read_key_nonblocking()

            # ======= KEY HANDLING =======
            if ch is not None:

                if ch == "q":
                    print("\nQuitting...")
                    break

                elif ch == " ":
                    print("[SPACE] Stop")
                    px.stop()
                    motion = "stop"

                elif ch == "w":
                    print(f"[W] Forward, steering={steering_angle}°")
                    px.set_dir_servo_angle(steering_angle)
                    px.forward(speed)
                    motion = "forward"

                elif ch == "s":
                    print(f"[S] Backward, steering={steering_angle}°")
                    px.set_dir_servo_angle(steering_angle)
                    px.backward(speed)
                    motion = "backward"

                elif ch == "a":
                    steering_angle -= STEER_STEP
                    steering_angle = clamp(steering_angle, -MAX_STEER, MAX_STEER)
                    px.set_dir_servo_angle(steering_angle)
                    print(f"[A] Steering LEFT → {steering_angle}° (no movement)")

                elif ch == "d":
                    steering_angle += STEER_STEP
                    steering_angle = clamp(steering_angle, -MAX_STEER, MAX_STEER)
                    px.set_dir_servo_angle(steering_angle)
                    print(f"[D] Steering RIGHT → {steering_angle}° (no movement)")

            # ======= ULTRASONIC SAFETY =======
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
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

        print("\nResetting motors and steering...")
        px.stop()
        px.set_dir_servo_angle(0)
        px.set_cam_pan_angle(0)
        px.set_cam_tilt_angle(0)
        px.close()


if __name__ == "__main__":
    main()
