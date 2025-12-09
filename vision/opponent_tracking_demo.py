#!/usr/bin/env python3

import time
from vilib import Vilib
from opponent_tracking import OpponentTracker

MODEL_PATH = "/opt/vilib/mobilenet_v1_0.25_224_quant.tflite"
LABELS_PATH = "/opt/vilib/labels_mobilenet_quant_v1_224.txt"


def main():
    # 1) Start camera
    Vilib.camera_start(vflip=False, hflip=False, size=(640, 480))

    # 2) Web display so you can see what the camera sees
    Vilib.display(local=False, web=True)

    # 3) Configure object detection model + labels
    print("[Demo] Setting object detection model/labels...")
    Vilib.object_detect_set_model(MODEL_PATH)
    Vilib.object_detect_set_labels(LABELS_PATH)
    Vilib.object_detect_switch(True)

    # 4) Create tracker and run debug loop
    tracker = OpponentTracker(
        camera_width=Vilib.camera_width,
        camera_height=Vilib.camera_height,
    )

    print("[Demo] Opponent tracking is running.")
    print("Open the stream in your browser, e.g. http://<pi-ip>:9000/mjpg")
    print("Watch terminal for combat state.\n")

    try:
        tracker.run_debug_loop(poll_rate=0.3)
    finally:
        Vilib.camera_close()
        time.sleep(0.5)


if __name__ == "__main__":
    main()
