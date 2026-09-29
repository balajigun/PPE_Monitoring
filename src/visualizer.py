"""
visualizer.py

Draws detection results on video frames.
"""
import cv2

class Visualizer:
    """
    Draws bounding boxes and labels.
    """

    def __init__(self):

        # BGR Colors
        self.box_color = (0, 255, 0)
        self.text_color = (255, 255, 255)
        self.text_background = (0, 255, 0)

        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.font_scale = 0.5
        self.thickness = 2

    def draw(self, frame, worker_status):
        """
        Draw worker status on a frame.
        """

        for worker in worker_status:

            person = worker["person"]

            x1, y1, x2, y2 = person.bbox

            track_id = worker["track_id"]
            status = worker["status"]

            # Choose color
            if status == "SAFE":
                box_color = (0, 255, 0)      # Green
            else:
                box_color = (0, 0, 255)      # Red

            label = f"ID {track_id} | {status}"

        # Draw bounding box
            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                box_color,
                self.thickness
            )

        # Get text size
            (text_width, text_height), _ = cv2.getTextSize(
                label,
                self.font,
                self.font_scale,
            1
            )

        # Draw label background
            cv2.rectangle(
                frame,
                (x1, y1 - text_height - 10),
                (x1 + text_width, y1),
                box_color,
                -1
            )

        # Draw label
            cv2.putText(
                frame,
                label,
                (x1, y1 - 5),
                self.font,
                self.font_scale,
                self.text_color,
                1,
                cv2.LINE_AA
            )

        return frame