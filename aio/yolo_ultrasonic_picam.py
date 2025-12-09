#!/usr/bin/env python3
import time
from ultralytics import YOLO
from picarx import Picarx

# NEW: use picamera2
from picamera2 import Picamera2

# Load YOLO nano model
model = YOLO("yolov8n.pt")

# Initialize PiCar-X for ultrasonic sensor
px = Picarx()


def get_distance_cm():
    d = px.get_distance()
    if d is None or d <= 0:
        return 999.0
    return float(d)


def main():
    # --- Camera setup with picamera2 ---
    picam2 = Picamera2()
    # 640x480 is plenty; RGB888 works well with YOLO
    config = picam2.create_preview_configuration(
        main={"format": "RGB888", "size": (640, 480)}
    )
    picam2.configure(config)
    picam2.start()
    time.sleep(2)  # let the camera warm up

    print("Starting YOLO + Ultrasonic (picamera2) demo. Ctrl+C to stop.")

    try:
        while True:
            # Capture a frame as a numpy array (RGB)
            frame = picam2.capture_array()

            # Run YOLO on the frame (smaller imgsz for speed)
            results = model(frame, imgsz=320, verbose=False)[0]

            # Get ultrasonic distance
            dist = get_distance_cm()

            # Pick best detection if any
            if len(results.boxes) > 0:
                best_box = max(results.boxes, key=lambda b: float(b.conf[0]))
                cls_id = int(best_box.cls[0])
                conf = float(best_box.conf[0])
                label = model.names[cls_id]
                print(
                    f"Det: {label:10s} conf={conf:.2f} | Ultrasonic: {dist:6.1f} cm",
                    end="\r",
                )
            else:
                print(
                    f"No detections        | Ultrasonic: {dist:6.1f} cm",
                    end="\r",
                )

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nStopping...")

    finally:
        picam2.stop()
        px.stop()


if __name__ == "__main__":
    main()
