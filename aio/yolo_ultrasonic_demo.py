#!/usr/bin/env python3
import time
import cv2
from ultralytics import YOLO
from picarx import Picarx

# Load YOLO nano model (pretrained on COCO)
model = YOLO("yolov8n.pt")

# Initialize camera (adjust index if needed)
cap = cv2.VideoCapture(0)

# Initialize PiCar-X for ultrasonic sensor
px = Picarx()

def get_distance_cm():
    d = px.get_distance()
    if d is None or d <= 0:
        return 999.0
    return float(d)

def main():
    if not cap.isOpened():
        print("Error: Cannot open camera.")
        return

    print("Starting YOLO + Ultrasonic demo. Press 'q' to quit.")
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame.")
                break

            # Run YOLO (small image size for speed)
            results = model(frame, imgsz=320, verbose=False)[0]

            # Draw detection boxes
            for box in results.boxes:
                xyxy = box.xyxy[0].tolist()  # [x1, y1, x2, y2]
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])

                x1, y1, x2, y2 = map(int, xyxy)
                label = f"{model.names[cls_id]} {conf:.2f}"

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, label, (x1, max(y1 - 5, 10)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

            # Read ultrasonic distance
            dist = get_distance_cm()

            # Overlay distance on frame
            text = f"Ultrasonic: {dist:.1f} cm"
            cv2.putText(frame, text, (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

            # Show frame
            cv2.imshow("PiCar-X YOLO + Ultrasonic", frame)

            # Press 'q' to quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print("\nInterrupted by user.")

    finally:
        cap.release()
        cv2.destroyAllWindows()
        px.stop()

if __name__ == "__main__":
    main()
