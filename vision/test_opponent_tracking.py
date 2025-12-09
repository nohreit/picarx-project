from opponent_tracking import OpponentTracker

# from OpponentTracking import OpponentTracker
from vilib import Vilib

# Start camera + web stream
Vilib.camera_start()
Vilib.display(local=False, web=True)

# Enable vilib detection model (optional)
Vilib.object_detect_set_model(
    "/home/primal/vilib/workspace/mobilenet_v1_0.25_224_quant.tflite"
)
Vilib.object_detect_set_labels("/home/primal/vilib/workspace/coco_labels.txt")
Vilib.object_detect_switch(True)

tracker = OpponentTracker()
tracker.run_with_vilib()
