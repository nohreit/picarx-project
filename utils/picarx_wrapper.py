from picarx import Picarx


class PX:
    def __init__(self):
        self.px = Picarx()

    def forward(self, speed=30):
        self.px.set_dir_servo_angle(0)
        self.px.forward(speed)

    def left(self, speed=30, angle=25):
        self.px.set_dir_servo_angle(-angle)
        self.px.forward(speed)

    def right(self, speed=30, angle=25):
        self.px.set_dir_servo_angle(angle)
        self.px.forward(speed)

    def stop(self):
        self.px.stop()
        self.px.set_dir_servo_angle(0)

    def center_camera(self):
        self.px.set_cam_pan_angle(0)
        self.px.set_cam_tilt_angle(0)
