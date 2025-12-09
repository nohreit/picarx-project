#!/usr/bin/env python3
import os
import sys
import time

import cv2
import numpy as np

# Make project root importable
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from utils.picarx_wrapper import PX

try:
    from ultralytics import YOLO
except ImportError:
    print("ERROR: ultralytics not installed. Run: pip3 install ultralytics")
    sys.exit(1)


# ---------------------- CONFIG -----------------------------------

MODEL_PATH = os.path.expanduser("~/picarx-project/models/yolov8n.pt")  # adjust to your path
CONF_THRESHOLD = 0.35  # YOLO confidence threshold
CENTER_REGION = 0.30  # fraction of image width treated as 'front'
ULTRASONIC_STOP_CM = 25.0  # stop distance
FORWARD_SPEED = 25  # base forward speed (0–100)
TURN_ANGLE = 25  # steering angle for avoidance
TURN_TIME = 0.5  # seconds to hold a turn

# If you want to limit which classes count as obstacles, you can
# set this to a list of indexes (e.g. [0] for person) or None for all:
OBSTACLE_CLASSES = None  # or something like [0, 1, 2]


# ---------------------- HELPERS ----------------------------------


def is_obstacle_in_front(detections, frame_width: int) -> bool:
    """
    Decide whether YOLO sees an obstacle in the central region of the image.
    detections: ultralytics Results.boxes
    """
    if detections is None or len(detections) == 0:
        return False

    center_x_min = frame_width * (0.5 - CENTER_REGION / 2)
    center_x_max = frame_width * (0.5 + CENTER_REGION / 2)

    for box in detections:
        cls_id = int(box.cls[0])
        conf = float(box.conf[0])
        if conf < CONF_THRESHOLD:
            continue
        if OBSTACLE_CLASSES is not None and cls_id not in OBSTACLE_CLASSES:
            continue

        x1, y1, x2, y2 = box.xyxy[0]
        box_center_x = (float(x1) + float(x2)) / 2.0

        if center_x_min <= box_center_x <= center_x_max:
            return True

    return False


# ---------------------- MAIN LOOP --------------------------------


def main():
    if not os.path.exists(MODEL_PATH):
        print(f"ERROR: model not found at {MODEL_PATH}")
        sys.exit(1)

    print(f"Loading YOLO model from: {MODEL_PATH}")
    model = YOLO(MODEL_PATH)

    # Open camera (0 = default)
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("ERROR: Could not open camera (/dev/video0).")
        sys.exit(1)

    car = PX()
    print("YOLO + Ultrasonic obstacle avoidance started.")
    print("Press Ctrl+C to stop.")

    try:
        last_turn_dir = 1  # 1 = right, -1 = left, to alternate turns

        while True:
            ret, frame = cap.read()
            if not ret:
                print("WARNING: Failed to grab frame.")
                time.sleep(0.1)
                continue

            h, w, _ = frame.shape

            # Run YOLO inference
            results = model.predict(
                frame,
                imgsz=320,  # smaller image for speed
                conf=CONF_THRESHOLD,
                verbose=False,
                device="cpu",
            )
            boxes = results[0].boxes if len(results) > 0 else None

            # Ultrasonic reading
            distance = car.get_distance_cm()

            yolo_front = is_obstacle_in_front(boxes, w)
            ultrasonic_close = (distance > 0) and (distance < ULTRASONIC_STOP_CM)

            # --- Decision logic -----------------------------------------
            if yolo_front or ultrasonic_close:
                car.stop()
                print(
                    f"\rObstacle! YOLO:{yolo_front} "
                    f"Ultrasonic:{distance:.1f if distance > 0 else -1}cm   ",
                    end="",
                    flush=True,
                )

                # Simple avoidance: turn a bit, then try forward again
                turn_dir = last_turn_dir
                steer_angle = TURN_ANGLE * turn_dir
                car.steer(steer_angle)
                time.sleep(0.1)
                car.backward(FORWARD_SPEED)  # small wiggle back
                time.sleep(TURN_TIME)
                car.stop()

                # Alternate direction next time
                last_turn_dir *= -1
                # Center steering back
                car.steer(0)

            else:
                # Clear path -> go forward
                car.steer(0)
                car.forward(FORWARD_SPEED)
                print(
                    f"\rClear. Distance:{distance:.1f if distance > 0 else -1}cm   ",
                    end="",
                    flush=True,
                )

            # small delay to avoid pegging CPU
            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\nStopping (Ctrl+C).")
    finally:
        car.cleanup()
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
