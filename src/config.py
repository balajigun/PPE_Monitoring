"""
Project configuration.

This file contains all configurable values such as
project paths, model paths, thresholds and display settings.
"""
from pathlib import Path

# =====================================================
# Project Root
# =====================================================
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# =====================================================
# Project Paths
# =====================================================
INPUT_VIDEO_DIR = PROJECT_ROOT / "data" / "input_videos"
OUTPUT_VIDEO_DIR = PROJECT_ROOT / "data" / "output_videos"
MODEL_DIR = PROJECT_ROOT / "models"
REPORT_DIR = PROJECT_ROOT / "reports"

# =====================================================
# Video
# =====================================================
VIDEO_NAME = "ppe_monitoring.mp4"
VIDEO_PATH = INPUT_VIDEO_DIR / VIDEO_NAME

OUTPUT_VIDEO_NAME = "output.mp4"
OUTPUT_VIDEO_PATH = OUTPUT_VIDEO_DIR / OUTPUT_VIDEO_NAME

# =====================================================
# Model
# =====================================================
MODEL_PATH = MODEL_DIR / "best.pt"

# =====================================================
# Detection Settings
# =====================================================
CONFIDENCE_THRESHOLD = 0.25
IOU_THRESHOLD = 0.45

# =====================================================
# Display
# =====================================================
WINDOW_NAME = "PPE Monitoring"
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720