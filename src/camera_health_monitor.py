"""
camera_health_monitor.py

Monitors camera/video stream health.

Current assessment:
    MP4 video is treated as the camera source.

Future production:
    Can be extended for RTSP connection and automatic reconnection.
"""

import time


class CameraHealthMonitor:

    def __init__(
        self,
        camera_id="CAMERA_01",
        expected_fps=15.0,
        frame_timeout_seconds=5.0
    ):

        self.camera_id = camera_id
        self.expected_fps = expected_fps
        self.frame_timeout_seconds = frame_timeout_seconds

        self.total_frames = 0

        self.last_frame_time = None
        self.last_frame_timestamp = None

        self.processing_start_time = None

        self.status = "INITIALIZING"

        self.actual_fps = 0.0

    # ============================================================
    # START MONITORING
    # ============================================================

    def start(self):

        self.processing_start_time = time.monotonic()

        self.last_frame_time = None
        self.last_frame_timestamp = None

        self.total_frames = 0

        self.status = "STARTING"

    # ============================================================
    # FRAME RECEIVED
    # ============================================================

    def frame_received(self, timestamp=None):

        current_time = time.monotonic()

        self.total_frames += 1

        self.last_frame_time = current_time
        self.last_frame_timestamp = timestamp

        if self.processing_start_time is not None:

            elapsed = (
                current_time -
                self.processing_start_time
            )

            if elapsed > 0:

                self.actual_fps = (
                    self.total_frames /
                    elapsed
                )

        # Camera/video source is producing frames
        self.status = "HEALTHY"

    # ============================================================
    # CHECK HEALTH
    # ============================================================

    def check_health(self):

        if self.last_frame_time is None:

            self.status = "NO_FRAME"

            return self.status

        elapsed_since_last_frame = (
            time.monotonic() -
            self.last_frame_time
        )

        if (
            elapsed_since_last_frame >
            self.frame_timeout_seconds
        ):

            self.status = "NO_FRAME"

        elif self.actual_fps < (
            self.expected_fps * 0.5
        ):

            self.status = "DEGRADED"

        else:

            self.status = "HEALTHY"

        return self.status

    # ============================================================
    # GET HEALTH INFORMATION
    # ============================================================

    def get_health(self):

        self.check_health()

        if self.last_frame_time is None:

            seconds_since_last_frame = None

        else:

            seconds_since_last_frame = (
                time.monotonic() -
                self.last_frame_time
            )

        return {
            "camera_id": self.camera_id,
            "status": self.status,
            "expected_fps": round(
                self.expected_fps,
                2
            ),
            "actual_fps": round(
                self.actual_fps,
                2
            ),
            "total_frames": self.total_frames,
            "seconds_since_last_frame": (
                round(
                    seconds_since_last_frame,
                    2
                )
                if seconds_since_last_frame is not None
                else None
            )
        }

    # ============================================================
    # PRINT STATUS
    # ============================================================

    def print_status(self):

        health = self.get_health()

        print(
            "\n========== CAMERA HEALTH =========="
        )

        print(
            f"Camera ID          : "
            f"{health['camera_id']}"
        )

        print(
            f"Status             : "
            f"{health['status']}"
        )

        print(
            f"Expected FPS       : "
            f"{health['expected_fps']}"
        )

        print(
            f"Actual FPS         : "
            f"{health['actual_fps']}"
        )

        print(
            f"Total Frames       : "
            f"{health['total_frames']}"
        )

        print(
            f"Last Frame Age     : "
            f"{health['seconds_since_last_frame']}"
        )

        print(
            "==================================="
        )