#!/usr/bin/env python3
import time
import cv2
from ultralytics import YOLO
from picarx import Picarx

# Load YOLO nano model
model = YOLO("yolov8n.pt")

# Init camera (try /dev/video0; change index if needed)
cap = cv2.VideoCapture(0)

px = Picarx()


def get_distance_cm():
    d = px.get_distance()
    if d is None or d <= 0:
        return 999.0
    return float(d)


def main():
    if not cap.isOpened():
        print("Error: Cannot open camera (/dev/video0).")
        return

    print("Starting YOLO + Ultrasonic text demo. Ctrl+C to stop.")
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame.")
                break

            # Run YOLO on the frame (smaller size for speed)
            results = model(frame, imgsz=320, verbose=False)[0]

            # Get ultrasonic distance
            dist = get_distance_cm()

            # Take the "best" detection if any
            if len(results.boxes) > 0:
                # pick box with highest confidence
                best_box = max(results.boxes, key=lambda b: float(b.conf[0]))
                cls_id = int(best_box.cls[0])
                conf = float(best_box.conf[0])
                label = model.names[cls_id]
                print(
                    f"Det: {label:10s} conf={conf:.2f} | Ultrasonic: {dist:6.1f} cm",
                    end="\r",
                )
            else:
                print(f"No detections        | Ultrasonic: {dist:6.1f} cm", end="\r")

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nStopping...")

    finally:
        cap.release()
        px.stop()


if __name__ == "__main__":
    main()
