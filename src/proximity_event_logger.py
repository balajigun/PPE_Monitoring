"""
proximity_event_logger.py

CSV logger for unsafe worker-machinery proximity events.
"""

import csv
import os


class ProximityEventLogger:
    """
    Logs confirmed unsafe proximity events into a CSV file.
    """

    def __init__(self, output_path):

        self.output_path = output_path

        # Create parent directory
        parent_dir = os.path.dirname(output_path)

        if parent_dir:
            os.makedirs(
                parent_dir,
                exist_ok=True
            )

        # Open CSV
        self.file = open(
            self.output_path,
            mode="w",
            newline="",
            encoding="utf-8"
        )

        self.writer = csv.writer(self.file)

        # CSV header
        self.writer.writerow([
            "timestamp",
            "frame",
            "worker_id",
            "machinery_id",
            "distance_pixels",
            "event"
        ])

        self.file.flush()

        print("Proximity Event Logger initialized.")
        print(
            f"Proximity Report: {self.output_path}"
        )

    def log_event(
        self,
        timestamp,
        frame_number,
        event
    ):
        """
        Log one confirmed proximity event.

        Parameters
        ----------
        timestamp : float
            Video timestamp in seconds.

        frame_number : int
            Current video frame.

        event : dict
            Event returned by ProximityDetector.
        """

        self.writer.writerow([
            round(timestamp, 2),
            frame_number,
            event.get("worker_id"),
            event.get("machinery_id"),
            event.get("distance_pixels"),
            event.get("event")
        ])

        # Immediately write to disk
        self.file.flush()

    def close(self):

        if self.file and not self.file.closed:
            self.file.close()

        print("Proximity Event Logger closed.")