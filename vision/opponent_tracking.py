#!/usr/bin/env python3

"""
Opponent tracking based on vilib + TFLite MobileNet/COCO.

This module:
- uses vilib's built-in object detection pipeline
- reads detection results
- exposes a clean CombatState for the rest of the robot (AI / control).
"""

import time
from vilib import Vilib

# Classes we'll treat as "opponents" for now
ENEMY_CLASS_IDS = {0, 1, 2, 3, 7}  # person, bicycle, car, motorcycle, truck


class CombatState:
    def __init__(self):
        self.has_target = False
        self.bbox = None  # (xmin, ymin, xmax, ymax)
        self.cx_norm = 0.0  # [-1, 1], 0 = center
        self.cy_norm = 0.0  # [-1, 1]
        self.angle_deg = 0.0  # left negative, right positive
        self.distance_hint = None  # arbitrary scale for now
        self.class_id = None
        self.score = None

    def __repr__(self):
        if not self.has_target:
            return "<CombatState: no target>"
        return (
            f"<CombatState: target class={self.class_id} "
            f"angle={self.angle_deg:.1f}° bbox={self.bbox} "
            f"score={self.score:.2f}>"
        )


class OpponentTracker:
    def __init__(self, camera_width=640, camera_height=480):
        self.w = camera_width
        self.h = camera_height
        self.state = CombatState()

    # ---- Internal helpers -------------------------------------------------

    def _update_from_bbox(self, xmin, ymin, xmax, ymax, class_id=None, score=None):
        # Clamp
        xmin = max(0, min(self.w, xmin))
        xmax = max(0, min(self.w, xmax))
        ymin = max(0, min(self.h, ymin))
        ymax = max(0, min(self.h, ymax))

        bbox_w = max(1, xmax - xmin)
        bbox_h = max(1, ymax - ymin)

        cx = xmin + bbox_w / 2.0
        cy = ymin + bbox_h / 2.0

        cx_norm = (cx - self.w / 2.0) / (self.w / 2.0)
        cy_norm = (cy - self.h / 2.0) / (self.h / 2.0)

        # Approx angle: assume ~90° FOV horizontally
        angle_deg = cx_norm * 45.0

        # Extremely rough distance proxy; bigger bbox_h -> closer
        distance_hint = 1.0 / bbox_h

        self.state.has_target = True
        self.state.bbox = (int(xmin), int(ymin), int(xmax), int(ymax))
        self.state.cx_norm = float(cx_norm)
        self.state.cy_norm = float(cy_norm)
        self.state.angle_deg = float(angle_deg)
        self.state.distance_hint = float(distance_hint)
        self.state.class_id = class_id
        self.state.score = float(score) if score is not None else None

    def _clear(self):
        self.state = CombatState()

    # ---- Public API -------------------------------------------------------

    def get_state(self):
        """Return the last computed combat state."""
        return self.state

    def update_from_vilib_detections(self):
        """
        Read detection results from vilib (object_detection_list_parameter)
        and update CombatState using the best enemy detection.
        """
        det_list = getattr(Vilib, "object_detection_list_parameter", None)

        if not det_list:
            self._clear()
            return

        # det_list format depends on SunFounder code, but usually something like:
        # [{"bbox": [xmin, ymin, xmax, ymax], "class_id": int, "score": float}, ...]
        # 1. Filter to enemy class IDs if possible
        enemy_dets = [
            d for d in det_list if d.get("class_id") in ENEMY_CLASS_IDS
        ] or det_list  # if no enemy found, just fallback to any detection

        # 2. Pick highest-score detection
        best = max(enemy_dets, key=lambda d: d.get("score", 0.0))

        bbox = best.get("bbox")
        if bbox and len(bbox) == 4:
            xmin, ymin, xmax, ymax = bbox
            self._update_from_bbox(
                xmin,
                ymin,
                xmax,
                ymax,
                class_id=best.get("class_id"),
                score=best.get("score", 0.0),
            )
        else:
            self._clear()

    def run_debug_loop(self, poll_rate=0.2):
        """
        Debug loop: continuously read vilib detections and print combat state.
        Use this for tuning thresholds and verifying things work.
        """
        print("[OpponentTracker] Debug tracking loop started (Ctrl+C to stop).")
        try:
            while True:
                self.update_from_vilib_detections()
                print(self.state)
                time.sleep(poll_rate)
        except KeyboardInterrupt:
            print("\n[OpponentTracker] Stopped.")
