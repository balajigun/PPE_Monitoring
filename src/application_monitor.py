"""
application_monitor.py

Monitors application-level performance for the
computer vision pipeline.
"""

import time


class ApplicationMonitor:

    def __init__(
        self,
        expected_fps=15.0,
        reporting_interval=5.0
    ):

        self.expected_fps = expected_fps
        self.reporting_interval = reporting_interval

        self.total_frames = 0
        self.total_processing_time = 0.0

        self.current_fps = 0.0
        self.current_latency_ms = 0.0

        self.error_count = 0

        self.interval_start_time = time.monotonic()
        self.interval_frames = 0
        self.interval_processing_time = 0.0

        self.status = "STARTING"

    # ============================================================
    # START
    # ============================================================

    def start(self):

        self.interval_start_time = time.monotonic()

        self.total_frames = 0
        self.total_processing_time = 0.0

        self.interval_frames = 0
        self.interval_processing_time = 0.0

        self.error_count = 0

        self.status = "RUNNING"

    # ============================================================
    # FRAME START
    # ============================================================

    def start_frame(self):

        return time.perf_counter()

    # ============================================================
    # FRAME END
    # ============================================================

    def end_frame(
        self,
        frame_start_time
    ):

        processing_time = (
            time.perf_counter() -
            frame_start_time
        )

        self.total_frames += 1

        self.total_processing_time += (
            processing_time
        )

        self.interval_frames += 1

        self.interval_processing_time += (
            processing_time
        )

        self.current_latency_ms = (
            processing_time * 1000.0
        )

        # Calculate instantaneous/rolling processing FPS
        if processing_time > 0:

            self.current_fps = (
                1.0 /
                processing_time
            )

        # Check whether it is time to update status
        elapsed_interval = (
            time.monotonic() -
            self.interval_start_time
        )

        if elapsed_interval >= self.reporting_interval:

            self.current_fps = (
                self.interval_frames /
                elapsed_interval
            )

            self.interval_start_time = (
                time.monotonic()
            )

            self.interval_frames = 0

            self.interval_processing_time = 0.0

        self._update_status()

    # ============================================================
    # RECORD ERROR
    # ============================================================

    def record_error(self):

        self.error_count += 1

        self.status = "ERROR"

    # ============================================================
    # STATUS
    # ============================================================

    def _update_status(self):

        if self.error_count > 0:

            self.status = "ERROR"

        elif self.current_fps < (
            self.expected_fps * 0.5
        ):

            self.status = "DEGRADED"

        else:

            self.status = "HEALTHY"

    # ============================================================
    # GET METRICS
    # ============================================================

    def get_metrics(self):

        average_latency_ms = 0.0

        if self.total_frames > 0:

            average_latency_ms = (
                self.total_processing_time /
                self.total_frames
            ) * 1000.0

        return {
            "status": self.status,
            "expected_fps": round(
                self.expected_fps,
                2
            ),
            "processing_fps": round(
                self.current_fps,
                2
            ),
            "current_latency_ms": round(
                self.current_latency_ms,
                2
            ),
            "average_latency_ms": round(
                average_latency_ms,
                2
            ),
            "processed_frames": (
                self.total_frames
            ),
            "error_count": self.error_count
        }

    # ============================================================
    # PRINT METRICS
    # ============================================================

    def print_metrics(self):

        metrics = self.get_metrics()

        print(
            "\n========== APPLICATION MONITOR =========="
        )

        print(
            f"Status             : "
            f"{metrics['status']}"
        )

        print(
            f"Expected FPS       : "
            f"{metrics['expected_fps']}"
        )

        print(
            f"Processing FPS     : "
            f"{metrics['processing_fps']}"
        )

        print(
            f"Current Latency    : "
            f"{metrics['current_latency_ms']} ms"
        )

        print(
            f"Average Latency    : "
            f"{metrics['average_latency_ms']} ms"
        )

        print(
            f"Processed Frames   : "
            f"{metrics['processed_frames']}"
        )

        print(
            f"Errors             : "
            f"{metrics['error_count']}"
        )

        print(
            "=========================================="
        )