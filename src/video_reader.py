"""
video_reader.py

Module:
    Handles video input from a file or RTSP stream.

Author:
    Balaji G

Description:
    This module provides a reusable VideoReader class that
    opens a video source, retrieves video properties, reads
    frames sequentially, and releases resources safely.
"""

from pathlib import Path
import cv2


class VideoReader:
    """
    VideoReader is responsible for reading frames from
    a video file or RTSP stream.
    """

    def __init__(self, video_source):
        """
        Parameters
        ----------
        video_source : str or Path
            Path to the video file or RTSP URL.
        """

        self.video_source = str(video_source)

        self.cap = None

        self.fps = 0
        self.width = 0
        self.height = 0
        self.total_frames = 0

    def open(self):
        """
        Opens the video source.

        Raises
        ------
        FileNotFoundError
            If the video file does not exist.

        RuntimeError
            If OpenCV cannot open the video.
        """

        # Only check file existence for local files.
        if not self.video_source.startswith("rtsp://"):
            if not Path(self.video_source).exists():
                raise FileNotFoundError(
                    f"Video not found:\n{self.video_source}"
                )

        self.cap = cv2.VideoCapture(self.video_source)

        if not self.cap.isOpened():
            raise RuntimeError(
                f"Unable to open video:\n{self.video_source}"
            )

        # Read video properties.
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.total_frames = int(
            self.cap.get(cv2.CAP_PROP_FRAME_COUNT)
        )

    def read(self):
        """
        Reads one frame.

        Returns
        -------
        success : bool
            True if a frame was read successfully.

        frame : numpy.ndarray or None
            Video frame.
        """

        if self.cap is None:
            raise RuntimeError(
                "Video is not opened. Call open() first."
            )

        success, frame = self.cap.read()

        return success, frame

    def release(self):
        """
        Releases video resources.
        """

        if self.cap is not None:
            self.cap.release()

    def get_video_info(self):
        """
        Returns video metadata.

        Returns
        -------
        dict
            Dictionary containing video information.
        """

        return {
            "fps": self.fps,
            "width": self.width,
            "height": self.height,
            "total_frames": self.total_frames,
        }