"""
detector.py

YOLO Detector Module

Loads the YOLO model once and performs object detection
on incoming video frames.
"""

from ultralytics import YOLO

from config import (
    MODEL_PATH,
    CONFIDENCE_THRESHOLD,
    IOU_THRESHOLD,
)

from detection import Detection

class Detector:
    """
    Wrapper around the Ultralytics YOLO detector.
    """

    def __init__(self):

        print("Loading YOLO model...")

        self.model = YOLO(MODEL_PATH)

        # Save class names once
        self.class_names = self.model.names

        print("YOLO model loaded successfully.")

    def detect(self, frame):
        """
        Runs object detection on a frame.

        Parameters
        ----------
        frame : numpy.ndarray

        Returns
        -------
        list[Detection]
        """

        results = self.model.track(
            frame,
            persist=True,
            tracker="configs/tracktrack_reid.yaml",
            conf=CONFIDENCE_THRESHOLD,
            iou=IOU_THRESHOLD,
            verbose=False
        )
        result = results[0]

        detections = []

        for box in result.boxes:

            class_id = int(box.cls.item())

            class_name = self.class_names[class_id]
            
            confidence = float(box.conf.item())

            x1, y1, x2, y2 = map(
                int,
                box.xyxy[0].tolist()
            )

            if box.id is not None:
                track_id = int(box.id.item())
            else:
                track_id = None
            
            detections.append(
                Detection(
                    class_id=class_id,
                    class_name=class_name,
                    confidence=confidence,
                    bbox=(x1, y1, x2, y2),
                    track_id=track_id           
                )
            )
        return detections