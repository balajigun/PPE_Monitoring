import cv2
import os

from config import (
    PROJECT_ROOT,
    INPUT_VIDEO_DIR,
    OUTPUT_VIDEO_DIR,
    MODEL_PATH,
    VIDEO_PATH,
)

from video_reader import VideoReader
from detector import Detector
from visualizer import Visualizer
from ppe_rules import PPERules
from ppe_state import PPEStateTracker
from csv_logger import CSVLogger
from worker_count_logger import WorkerCountLogger
from alert_manager import AlertManager
from proximity_detector import ProximityDetector
from proximity_event_logger import ProximityEventLogger
from logging_setup import setup_logging

# ============================================================
# SYSTEM MONITORING
# ============================================================

from camera_health_monitor import CameraHealthMonitor
from application_monitor import ApplicationMonitor
from gpu_monitor import GPUMonitor


def main():

    log_file = setup_logging()
    print("=" * 60)
    print("PPE Monitoring System")
    print("=" * 60)

    print(f"Project Root : {PROJECT_ROOT}")
    print(f"Input Videos : {INPUT_VIDEO_DIR}")
    print(f"Output Videos: {OUTPUT_VIDEO_DIR}")
    print(f"Model Path   : {MODEL_PATH}")

    # ============================================================
    # INITIALIZE VIDEO READER
    # ============================================================

    print("\nOpening Video...\n")

    reader = VideoReader(VIDEO_PATH)
    reader.open()

    # ============================================================
    # VIDEO INFORMATION
    # ============================================================

    info = reader.get_video_info()

    print("=" * 60)
    print("Video Information")
    print("=" * 60)

    print(f"FPS          : {info['fps']:.2f}")
    print(f"Width        : {info['width']}")
    print(f"Height       : {info['height']}")
    print(f"Total Frames : {info['total_frames']}")

    print(
        f"[VIDEO INFO] "
        f"width={info['width']}, "
        f"height={info['height']}, "
        f"fps={info['fps']}"
    )

    # ============================================================
    # CREATE OUTPUT DIRECTORY
    # ============================================================

    os.makedirs(
        OUTPUT_VIDEO_DIR,
        exist_ok=True
    )

    # ============================================================
    # OUTPUT VIDEO
    # ============================================================

    output_video_path = os.path.join(
        OUTPUT_VIDEO_DIR,
        "ocsort_output_3.mp4"
    )

    print(
        f"\nOutput Video : "
        f"{output_video_path}"
    )

    # ============================================================
    # VIDEO WRITER
    # ============================================================

    fourcc = cv2.VideoWriter_fourcc(
        *"mp4v"
    )

    writer = cv2.VideoWriter(
        output_video_path,
        fourcc,
        info["fps"],
        (
            info["width"],
            info["height"]
        )
    )

    if not writer.isOpened():

        raise RuntimeError(
            f"VideoWriter failed to open: "
            f"{output_video_path}"
        )

    print(
        "[WRITER] VideoWriter opened successfully"
    )

    print(
        f"[WRITER] Frame size = "
        f"{info['width']} x "
        f"{info['height']}"
    )

    print(
        f"[WRITER] FPS = "
        f"{info['fps']}"
    )

    # ============================================================
    # CAMERA HEALTH MONITOR
    # ============================================================

    camera_monitor = CameraHealthMonitor(
        camera_id="CAMERA_01",
        expected_fps=info["fps"],
        frame_timeout_seconds=5.0
    )

    camera_monitor.start()

    print(
        "\n[MONITOR] Camera Health Monitor initialized."
    )

    # ============================================================
    # APPLICATION MONITOR
    # ============================================================

    application_monitor = ApplicationMonitor(
        expected_fps=info["fps"],
        reporting_interval=5.0
    )

    application_monitor.start()

    print(
        "[MONITOR] Application Monitor initialized."
    )

    # ============================================================
    # GPU MONITOR
    # ============================================================

    gpu_monitor = GPUMonitor()

    print(
        "[MONITOR] GPU Monitor initialized."
    )

    # ============================================================
    # INITIALIZE DETECTOR
    # ============================================================

    print("\nLoading detector...\n")

    detector = Detector()

    # ============================================================
    # PPE RULES
    # ============================================================

    ppe_rules = PPERules()

    # ============================================================
    # PPE STATE TRACKER
    # ============================================================

    reentry_tolerance_frames = max(
        30,
        int(
            round(
                info["fps"] * 5
            )
        )
    )

    ppe_state = PPEStateTracker(
        max_missing_frames=
        reentry_tolerance_frames
    )

    print(
        f"Worker re-entry tolerance: "
        f"{reentry_tolerance_frames} frames "
        f"(~"
        f"{reentry_tolerance_frames / info['fps']:.1f}"
        f" sec)"
    )

    # ============================================================
    # VISUALIZER
    # ============================================================

    visualizer = Visualizer()

    # ============================================================
    # ALERT MANAGER
    # ============================================================

    alert_manager = AlertManager(
        smtp_server="smtp.gmail.com",
        smtp_port=587,
        sender_email=os.getenv(
            "PPE_SENDER_EMAIL"
        ),
        sender_password=os.getenv(
            "PPE_EMAIL_PASSWORD"
        ),
        supervisor_email=os.getenv(
            "PPE_SUPERVISOR_EMAIL"
        ),
        screenshot_dir=os.path.join(
            PROJECT_ROOT,
            "alerts"
        ),
        cooldown_seconds=60
    )

    # ============================================================
    # REPORT DIRECTORY
    # ============================================================

    report_dir = os.path.join(
        PROJECT_ROOT,
        "reports"
    )

    os.makedirs(
        report_dir,
        exist_ok=True
    )

    # ============================================================
    # PPE CSV LOGGER
    # ============================================================

    report_path = os.path.join(
        report_dir,
        "video_1_report.csv"
    )

    csv_logger = CSVLogger(
        report_path
    )

    # ============================================================
    # TASK 1 WORKER COUNT LOGGER
    # ============================================================

    worker_count_report_path = os.path.join(
        report_dir,
        "task1_worker_count.csv"
    )

    worker_count_logger = WorkerCountLogger(
        worker_count_report_path
    )

    # ============================================================
    # UNSAFE PROXIMITY DETECTOR
    # ============================================================

    proximity_detector = ProximityDetector(
        safety_zone_margin=200,
        confirmation_frames=5,
        machinery_classes={
            "machinery"
        }
    )

    # ============================================================
    # PROXIMITY EVENT REPORT
    # ============================================================

    proximity_report_path = os.path.join(
        report_dir,
        "proximity_events.csv"
    )

    proximity_logger = ProximityEventLogger(
        proximity_report_path
    )

    # ============================================================
    # FRAME LOOP
    # ============================================================

    frame_number = 0

    while True:

        # ========================================================
        # START APPLICATION FRAME TIMER
        # ========================================================

        frame_start_time = (
            application_monitor.start_frame()
        )

        # ========================================================
        # READ FRAME
        # ========================================================

        success, frame = reader.read()

        if not success:

            print(
                "End of video reached."
            )

            break

        frame_number += 1

        # ========================================================
        # TIMESTAMP
        # ========================================================

        timestamp_seconds = (
            frame_number - 1
        ) / info["fps"]

        # ========================================================
        # CAMERA HEALTH
        # ========================================================

        camera_monitor.frame_received(
            timestamp=timestamp_seconds
        )

        # ========================================================
        # FRAME DEBUG
        # ========================================================

        print(
            f"\n========== FRAME "
            f"{frame_number} =========="
        )

        # ========================================================
        # DETECTION + TRACKING
        # ========================================================

        try:

            detections = detector.detect(
                frame
            )

        except Exception as e:

            application_monitor.record_error()

            print(
                f"[APPLICATION ERROR] "
                f"Detection failed: {e}"
            )

            continue

        # ========================================================
        # TASK 1 - WORKER COUNT
        # ========================================================

        worker_count = sum(
            1
            for detection in detections
            if (
                detection.class_name.lower()
                == "person"
            )
        )

        worker_count_logger.log_frame(
            frame_number,
            timestamp_seconds,
            worker_count
        )

        # ========================================================
        # PPE EVALUATION
        # ========================================================

        worker_status = (
            ppe_rules.evaluate(
                detections
            )
        )

        # ========================================================
        # STABLE WORKER ID / PPE STATE
        # ========================================================

        worker_status = (
            ppe_state.update(
                worker_status
            )
        )

        # ========================================================
        # UNSAFE PROXIMITY DETECTION
        # ========================================================

        machinery = [
            detection
            for detection in detections
            if (
                detection.class_name.lower()
                == "machinery"
            )
        ]

        proximity_events = (
            proximity_detector.detect(
                worker_status,
                machinery
            )
        )

        # ========================================================
        # LOG PROXIMITY EVENTS
        # ========================================================

        for event in proximity_events:

            proximity_logger.log_event(
                timestamp=timestamp_seconds,
                frame_number=frame_number,
                event=event
            )

            print(
                f"[PROXIMITY EVENT] "
                f"Frame={frame_number} "
                f"Worker={event['worker_id']} "
                f"Machinery={event['machinery_id']} "
                f"Distance="
                f"{event['distance_pixels']} px"
            )

        # ========================================================
        # PPE CSV REPORT
        # ========================================================

        csv_logger.log_frame(
            ppe_state.frame_number,
            timestamp_seconds,
            worker_status
        )

        # ========================================================
        # DEBUG DETECTIONS
        # ========================================================

        for detection in detections:

            print(detection)

        # ========================================================
        # DRAW VISUALIZATION
        # ========================================================

        frame = visualizer.draw(
            frame,
            worker_status
        )

        # ========================================================
        # PPE ALERT PROCESSING
        # ========================================================

        for worker in worker_status:

            violations = worker.get(
                "confirmed_violations",
                []
            )

            alert_manager.process_alert(
                frame=frame,
                frame_number=
                ppe_state.frame_number,
                worker_id=
                worker["stable_worker_id"],
                violations=violations
            )

        # ========================================================
        # FRAME SIZE VALIDATION
        # ========================================================

        expected_height = info["height"]
        expected_width = info["width"]

        actual_height = frame.shape[0]
        actual_width = frame.shape[1]

        if (
            actual_height != expected_height
            or
            actual_width != expected_width
        ):

            print(
                "[WARNING] "
                "Frame size mismatch!"
            )

            print(
                f"Expected : "
                f"{expected_width} x "
                f"{expected_height}"
            )

            print(
                f"Actual   : "
                f"{actual_width} x "
                f"{actual_height}"
            )

            frame = cv2.resize(
                frame,
                (
                    expected_width,
                    expected_height
                )
            )

            print(
                "[FRAME FIX] "
                "Frame resized."
            )

        # ========================================================
        # WRITE OUTPUT VIDEO
        # ========================================================

        writer.write(
            frame
        )

        if frame_number == 1:

            print(
                "[VIDEO WRITE] "
                "Frame 1 written successfully"
            )

            print(
                f"[FRAME DEBUG] "
                f"Shape={frame.shape}"
            )

            print(
                f"[FRAME DEBUG] "
                f"WriterOpened="
                f"{writer.isOpened()}"
            )

        if frame_number % 100 == 0:

            print(
                f"[VIDEO WRITE] "
                f"Frame {frame_number} written"
            )

        # ========================================================
        # APPLICATION MONITOR
        # ========================================================

        application_monitor.end_frame(
            frame_start_time
        )

        # ========================================================
        # PERIODIC MONITORING
        #
        # Approximately every 5 seconds
        # ========================================================

        monitoring_interval_frames = max(
            1,
            int(
                round(
                    info["fps"] * 5
                )
            )
        )

        if (
            frame_number %
            monitoring_interval_frames
            == 0
        ):

            print(
                "\n"
                + "=" * 60
            )

            print(
                "SYSTEM HEALTH MONITORING"
            )

            print(
                "=" * 60
            )

            # ----------------------------------------------------
            # CAMERA
            # ----------------------------------------------------

            camera_monitor.print_status()

            # ----------------------------------------------------
            # APPLICATION
            # ----------------------------------------------------

            application_monitor.print_metrics()

            # ----------------------------------------------------
            # GPU
            # ----------------------------------------------------

            gpu_monitor.print_metrics()

            print(
                "=" * 60
            )

        # ========================================================
        # DISPLAY
        # ========================================================

        cv2.imshow(
            "PPE Monitoring",
            frame
        )

        # ========================================================
        # PRESS Q TO EXIT
        # ========================================================

        if (
            cv2.waitKey(1) & 0xFF
            == ord("q")
        ):

            print(
                "Stopped by user."
            )

            break

    # ============================================================
    # FINAL APPLICATION METRICS
    # ============================================================

    print(
        "\n"
        + "=" * 60
    )

    print(
        "FINAL SYSTEM HEALTH"
    )

    print(
        "=" * 60
    )

    camera_monitor.print_status()

    application_monitor.print_metrics()

    gpu_monitor.print_metrics()

    # ============================================================
    # CLEANUP
    # ============================================================

    print(
        "\nStarting cleanup..."
    )

    reader.release()

    writer.release()

    cv2.destroyAllWindows()

    csv_logger.close()

    worker_count_logger.close()

    proximity_logger.close()

    gpu_monitor.close()

    # ============================================================
    # FINAL REPORT PATHS
    # ============================================================

    print(
        "\nTask 1 worker-count report saved to:"
    )

    print(
        worker_count_report_path
    )

    print(
        "\nOutput video saved to:"
    )

    print(
        output_video_path
    )

    print(
        "\nProximity event report saved to:"
    )

    print(
        proximity_report_path
    )

    # ============================================================
    # FINAL VIDEO FILE CHECK
    # ============================================================

    if os.path.exists(
        output_video_path
    ):

        output_size = os.path.getsize(
            output_video_path
        )

        print(
            "\n[VIDEO FILE CHECK]"
        )

        print(
            f"File size: "
            f"{output_size} bytes"
        )

        if output_size <= 257:

            print(
                "[WARNING] "
                "Output video file is extremely small."
            )

        else:

            print(
                "[SUCCESS] "
                "Output video contains data."
            )

    else:

        print(
            "[ERROR] "
            "Output video file was not created."
        )

    print(
        "\nVideo released successfully."
    )

    # ============================================================
    # END LOGGING
    # ============================================================

    print("=" * 70)
    print("PPE MONITORING APPLICATION FINISHED")
    print("=" * 70)

    log_file.close()

if __name__ == "__main__":

    main()