from picarx import Picarx
from vilib import Vilib
import time


def main():
    # Initialize robot (mainly to ensure hardware is ready)
    px = Picarx()

    # Start the camera
    Vilib.camera_start()

    # Optional: show FPS overlay
    Vilib.show_fps()

    # Start the built-in display
    Vilib.display()

    print("Camera preview running. Press Ctrl+C to stop.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        Vilib.camera_close()
        px.close()


if __name__ == "__main__":
    main()
