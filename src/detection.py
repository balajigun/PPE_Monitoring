"""
detection.py

Defines a standard Detection object used throughout the
PPE Monitoring System.

Instead of exposing YOLO's internal output format,
every detector converts its results into Detection objects.
"""

from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass
class Detection:
    """
    Represents a single detected object.
    """

    class_id: int
    class_name: str
    confidence: float
    bbox: Tuple[int, int, int, int]

    # Assigned by tracker
    track_id: Optional[int] = None