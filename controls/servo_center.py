from picarx import Picarx
import time

px = Picarx()

print("Centering steering (direction) servo to 0°...")
px.set_dir_servo_angle(0)
time.sleep(1)

print("Centering camera PAN servo to 0°...")
px.set_cam_pan_angle(0)
time.sleep(1)

print("Centering camera TILT servo to 0°...")
px.set_cam_tilt_angle(0)
time.sleep(1)

print("All servos centered. Adjust offsets as needed.") # 
