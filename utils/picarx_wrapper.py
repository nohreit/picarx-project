"""Wrapper for SunFounder PiCar-X."""
from picarx import Picarx


class PX:
    """Unified wrapper for SunFounder PiCar-X."""

    def __init__(self):
        self.robot = Picarx()

    # --- Motion -----------------------------------------------------------

    def forward(self, speed: int = 30):
        self.robot.forward(speed)

    def backward(self, speed: int = 30):
        self.robot.backward(speed)

    def stop(self):
        self.robot.stop()

    def steer(self, angle: float):
        """
        Angle in degrees: negative = left, positive = right.
        """
        self.robot.set_dir_servo_angle(angle)

    # --- Sensors ----------------------------------------------------------

    def get_distance_cm(self) -> float:
        """
        Returns distance in cm from the ultrasonic sensor.
        SunFounder API usually provides this.
        """
        try:
            d = self.robot.get_distance()
        except Exception:
            d = -1
        return d

    # --- Cleanup ----------------------------------------------------------

    def cleanup(self):
        s
