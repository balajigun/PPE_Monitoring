import csv
import os


class WorkerCountLogger:
    """
    Logs the number of detected workers for each video frame.

    Task 1 output:
        frame
        timestamp_seconds
        worker_count
    """

    def __init__(self, report_path):
        self.report_path = report_path

        report_dir = os.path.dirname(self.report_path)
        if report_dir:
            os.makedirs(report_dir, exist_ok=True)

        self.file = open(
            self.report_path,
            "w",
            newline="",
            encoding="utf-8"
        )

        self.writer = csv.writer(self.file)

        self.writer.writerow(
            [
                "frame",
                "timestamp_seconds",
                "worker_count"
            ]
        )

        self.file.flush()

        print("Worker Count Logger initialized.")
        print(
            f"Worker Count Report: "
            f"{self.report_path}"
        )

    def log_frame(
        self,
        frame_number,
        timestamp_seconds,
        worker_count
    ):
        """
        Write one worker-count record.
        """

        self.writer.writerow(
            [
                frame_number,
                f"{timestamp_seconds:.3f}",
                worker_count
            ]
        )

        self.file.flush()

    def close(self):
        """
        Close the CSV file safely.
        """

        if self.file and not self.file.closed:
            self.file.close()
