"""
csv_logger.py

CSV Logger Module

Stores frame-by-frame PPE status for each worker.
"""

import csv
import os


class CSVLogger:
    """
    Logs final worker-level PPE status into a CSV file.
    """

    def __init__(self, output_path):
        """
        Parameters
        ----------
        output_path : str
            Path where the CSV report will be created.
        """

        self.output_path = output_path

        # Create parent directory
        parent_dir = os.path.dirname(output_path)

        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)

        # Open CSV file
        self.file = open(
            self.output_path,
            mode="w",
            newline="",
            encoding="utf-8"
        )

        self.writer = csv.writer(self.file)

        # CSV header
        self.writer.writerow([
            "frame",
            "timestamp_seconds",
            "worker_id",
            "tracker_id",
            "helmet",
            "vest",
            "mask",
            "status"
        ])

        self.file.flush()

        print("CSV Logger initialized.")
        print(f"CSV Report: {self.output_path}")

    def log_frame(self, frame_number, timestamp_seconds, worker_status):
        """
        Logs all workers detected in the current frame.

        Parameters
        ----------
        frame_number : int
            Current video frame number.

        worker_status : list[dict]
            Output returned by PPEStateTracker.update().
        """

        for worker in worker_status:

            # Canonical worker ID
            worker_id = worker.get(
                "stable_worker_id",
                worker.get("track_id")
            )

            helmet = worker.get(
                "helmet",
                False
            )

            vest = worker.get(
                "vest",
                False
            )

            mask = worker.get(
                "mask",
                False
            )

            status = worker.get(
                "status",
                "MONITORING"
            )

            tracker_id = worker.get("tracker_id")

            self.writer.writerow([
                frame_number,
                f"{timestamp_seconds:.3f}",
                worker_id,
                tracker_id,
                helmet,
                vest,
                mask,
                status
            ])

        # Immediately save data to disk
        self.file.flush()

    def close(self):
        """
        Safely closes the CSV file.
        """

        if self.file and not self.file.closed:
            self.file.close()

        print("CSV Logger closed.")