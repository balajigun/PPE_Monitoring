# 🚧 Real-Time PPE Safety Monitoring System

A real-time **Computer Vision based PPE Safety Monitoring System** designed to detect workers, track worker identities, monitor Personal Protective Equipment (PPE) compliance, detect safety violations, capture violation evidence, generate reports, and send automated email alerts.

The system is designed as a modular video analytics pipeline that can be extended from a single-camera prototype to a multi-camera industrial safety monitoring platform.

---

## 📌 Project Overview

Construction and industrial environments require continuous monitoring to ensure that workers follow mandatory safety procedures.

Manual monitoring can be difficult to scale across large work areas and multiple cameras. This project implements an automated computer vision pipeline capable of analyzing video streams and identifying PPE-related safety violations.

The current system performs the following operations:

* 👷 Worker detection
* 👥 Worker counting
* 🆔 Worker tracking
* 🔄 Worker identity association
* 🪖 Helmet detection
* 🦺 Safety vest detection
* 😷 Mask detection
* ⚠️ PPE violation detection
* 📸 Violation screenshot capture
* 📧 Automated email alerts
* 📊 CSV-based reporting
* 🎥 Annotated output video generation
* 👥 Worker count logging
* Unsafe proximity detection between workers and heavy equipment
* 📄 Proximity event logging
* ❤️ Camera/stream health monitoring
* ⚙️ Application health monitoring
* 🖥️ GPU monitoring interface
* 📝 Timestamped application logging

The architecture is modular so that additional safety rules such as unsafe proximity between workers and heavy equipment can be integrated without redesigning the complete pipeline.

---

## Quick Start

### 1. Clone the repository

git clone https://github.com/balajigun/PPE_Monitoring.git

cd PPE_Monitoring

### 2. Install dependencies

pip install -r requirements.txt

### 3. Add model

Place the trained model at:

models/best.pt

### 4. Add input video

Place the input video at:

data/input_videos/ppe_monitoring.mp4

### 5. Run

python src/main.py

# 🎯 Objectives

The primary objectives of this project are:

1. Detect all workers present in the camera view.
2. Assign and maintain unique worker identities across video frames.
3. Associate PPE detections with individual workers.
4. Monitor helmet, safety vest, and mask compliance.
5. Detect missing PPE using temporal confirmation.
6. Capture visual evidence whenever a violation is detected.
7. Generate structured CSV reports.
8. Send automated email alerts to supervisors.
9. Produce an annotated output video for visual verification.
10. Detect unsafe proximity between workers and heavy equipment.
11. Monitor camera/stream health.
12. Monitor application processing health.
13. Capture operational logs for debugging and diagnostics.
14. Provide GPU monitoring hooks for supported environments.
15. Provide a Docker-based deployment path.
16. Provide a scalable architecture suitable for industrial deployment.
17. Provide a design path toward multi-camera and edge-AI deployment.

---

# 🏗️ System Architecture

The current application follows the pipeline:

```text
Input Video / Camera Stream
          │
          ▼
┌─────────────────────────┐
│       VideoReader       │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│      YOLO Detector      │
│       + OC-SORT         │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│    Detection Objects    │
│ Worker + PPE + Machine  │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│    PPE Association      │
│        Rules            │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│    PPE State Tracker    │
│   Temporal Validation   │
└────────────┬────────────┘
             │
       ┌─────┼───────────────┬─────────────────┐
       │     │               │                 │
       ▼     ▼               ▼                 ▼
     CSV   Worker Count   Alert Manager   Proximity Detector
                               │                 │
                               ├─ Screenshot     ├─ Worker
                               └─ Email          └─ Machinery
                                                   │
                                                   ▼
                                          Proximity Event Logger

             ┌─────────────────────────────────────────┐
             │          Visualization Layer            │
             │       Annotated Output Video            │
             └─────────────────────────────────────────┘

             ┌─────────────────────────────────────────┐
             │           System Health Layer            │
             │                                         │
             │ Camera Health Monitor                   │
             │ Application Monitor                     │
             │ GPU Monitor                              │
             │ Application Logging                     │
             └─────────────────────────────────────────┘
---

# 🔍 PPE Detection

The system uses a YOLO-based object detection model stored as:

```text
models/best.pt
```

The detector identifies workers and PPE-related classes.

The current PPE classes include:

| Class            | Purpose                   |
| ---------------- | ------------------------- |
| `Person`         | Worker detection          |
| `Hardhat`        | Positive helmet detection |
| `NO-Hardhat`     | Missing helmet evidence   |
| `Safety Vest`    | Positive vest detection   |
| `NO-Safety Vest` | Missing vest evidence     |
| `Mask`           | Positive mask detection   |
| `NO-Mask`        | Missing mask evidence     |

The model returns:

* Class ID
* Class name
* Confidence score
* Bounding box
* Tracking ID

These detections are converted into internal `Detection` objects before being passed to the PPE rule engine.

---

# 👷 Worker Detection

Worker detection is performed using the `Person` class from the YOLO model.

For every processed frame, the system identifies the workers currently visible in the camera view.

The worker count is logged with:

* Frame number
* Timestamp
* Number of detected workers

Example:

```text
frame,timestamp_seconds,worker_count
1,0.000,3
2,0.033,3
3,0.067,3
...
```

The worker count report is generated as:

```text
reports/task1_worker_count.csv
```

This supports the worker detection and counting requirement of the assessment.

---

# 🆔 Worker Tracking

Worker tracking is implemented using **TrackTrack** integrated with the YOLO detection pipeline.

The tracker provides a temporary tracking ID for each detected worker.

Example:

```text
Frame 100 → Worker Tracker ID = 3
Frame 101 → Worker Tracker ID = 3
Frame 102 → Worker Tracker ID = 3
```

Tracking allows PPE observations from consecutive frames to be associated with the same worker.

The tracker also helps maintain worker identity when workers move through the scene.

---

# 🔄 Worker Identity Association

A tracking ID generated by the object tracker can occasionally change because of:

* Occlusion
* Missed detections
* Crowded scenes
* Temporary disappearance
* Re-entry into the camera view
* Similar-looking workers

To address this, the system contains a separate **PPE State Tracker** responsible for maintaining a canonical worker identity.

The identity association mechanism considers:

### 1. IoU

Intersection over Union between the current worker bounding box and the previously observed bounding box.

```text
IoU = Area of Intersection / Area of Union
```

### 2. Center Distance

The distance between the center points of the current and previous bounding boxes is normalized relative to the worker bounding-box dimensions.

### 3. Missing Frame Tolerance

A worker identity is retained for a configurable number of frames even if the worker is temporarily not detected.

### 4. One-to-One Assignment

A previous worker identity is assigned to only one current detection during an association step.

This reduces accidental merging of two workers into one identity.

The association process can be represented as:

```text
Current Detection
       │
       ▼
Known Tracker ID?
   │          │
  Yes         No
   │          │
   ▼          ▼
Use ID     Search Previous Workers
                │
                ▼
        IoU + Center Distance
                │
        ┌───────┴────────┐
        │                │
     Match            No Match
        │                │
        ▼                ▼
Existing ID          New Worker ID
```

---

# 🧩 PPE Association Logic

Detecting PPE objects independently is not sufficient.

The system must determine which PPE item belongs to which worker.

The PPE rule engine therefore associates PPE detections with worker bounding boxes.

## Worker Bounding Box

For every worker:

```text
+---------------------------+
|           HEAD            |
|      Helmet / No Helmet   |
|                           |
|---------------------------|
|          TORSO            |
|    Safety Vest / No Vest  |
|                           |
|---------------------------|
|          LEGS             |
|                           |
+---------------------------+
```

The current implementation uses spatial relationships between PPE bounding boxes and the worker bounding box.

### Helmet Association

Helmet detections are expected inside the upper/head region of the worker.

The head region is approximately the upper portion of the worker bounding box.

### Safety Vest Association

Safety vest detections are evaluated primarily inside the torso region.

The torso region covers the central portion of the worker bounding box.

### Negative PPE Classes

The model also provides explicit negative classes:

```text
NO-Hardhat
NO-Safety Vest
NO-Mask
```

These detections provide direct evidence of missing PPE.

---

# ⏱️ Temporal PPE State Tracking

Single-frame PPE detection can produce false positives or false negatives because of:

* Motion blur
* Occlusion
* Poor lighting
* Detection confidence fluctuations
* Temporary object overlap
* Partial visibility

Therefore, the system does not immediately declare a violation from a single frame.

The `PPEStateTracker` maintains a short history of PPE observations for every worker.

Current implementation uses temporal history for:

```text
Helmet
Vest
Mask
```

The tracker maintains recent observations and confirms violations only when sufficient evidence is available.

The current violation threshold is based on repeated observations across the history window.

Conceptually:

```text
Frame 1 → NO Helmet
Frame 2 → NO Helmet
Frame 3 → NO Helmet
Frame 4 → Helmet
Frame 5 → NO Helmet

        ↓

Temporal evaluation

        ↓

Confirmed violation
```

This approach reduces the impact of isolated incorrect detections.

---

# ⚠️ Violation Detection

The system evaluates the PPE state of every tracked worker.

Supported violation categories include:

```text
NO HARDHAT
NO SAFETY VEST
NO MASK
```

The worker state can be:

```text
MONITORING
SAFE
NO HARDHAT
NO SAFETY VEST
NO MASK
```

Multiple violations can also be reported simultaneously.

Example:

```text
NO HARDHAT | NO SAFETY VEST
```

The violation state is generated from temporally confirmed PPE observations.

---

# 📸 Violation Evidence

When a PPE violation is confirmed, the system captures a screenshot of the relevant video frame.

The screenshot provides visual evidence for:

* Worker identity
* Detected violation
* Worker bounding box
* PPE detection state
* Scene context
* Timestamp

Screenshots are stored under:

```text
alerts/
```

This evidence can be used for:

* Supervisor review
* Incident investigation
* Safety reporting
* Audit purposes

---

# 📧 Automated Email Alerts

The project contains an `AlertManager` module for automated safety alerts.

When a confirmed PPE violation occurs, the alert manager can:

1. Detect the violation.
2. Capture a screenshot.
3. Apply alert cooldown logic.
4. Generate an email.
5. Attach the violation screenshot.
6. Send the alert to the configured supervisor.

The email system uses Gmail SMTP with STARTTLS.

```text
SMTP Server : smtp.gmail.com
SMTP Port   : 587
Protocol    : STARTTLS
```

For Gmail accounts, an **App Password** should be used instead of the normal account password.

---

# ⏳ Alert Cooldown

Continuous video processing can produce the same violation across many consecutive frames.

Without cooldown logic, this could generate hundreds of emails for a single incident.

Therefore, the alert manager applies a configurable cooldown period.

Current configuration:

```text
cooldown_seconds = 60
```

Conceptually:

```text
Violation detected
       │
       ▼
Was same alert recently sent?
       │
   ┌───┴───┐
  Yes      No
   │        │
   ▼        ▼
Ignore    Screenshot
             │
             ▼
           Email
             │
             ▼
       Record alert time
```
🚧 Unsafe Proximity Detection

The project includes an implemented unsafe proximity detection module for worker-to-heavy-equipment safety monitoring.

The objective is to identify situations where a worker enters a configurable safety zone around heavy equipment.

Detection Approach

The current implementation uses image-space geometry:

Detect and track workers.
Detect and track heavy machinery.
Calculate the worker's bottom-center/foot point.
Expand the machinery bounding box by a configurable safety margin.
Check whether the worker foot point enters the machinery safety zone.
Require the condition to persist for a configurable number of consecutive frames.
Generate a confirmed unsafe-proximity event.

Conceptually:

Worker Detection
       │
       ▼
Heavy Equipment Detection
       │
       ▼
Track Worker + Equipment
       │
       ▼
Worker Foot Point
       │
       ▼
Expanded Machinery Safety Zone
       │
       ▼
Spatial Proximity Check
       │
       ▼
Temporal Confirmation
       │
       ▼
UNSAFE PROXIMITY EVENT
       │
       └── CSV Event
The implementation uses configurable parameters such as:

safety_zone_margin
confirmation_frames
machinery_classes

The proximity event report is generated under:

reports/proximity_events.csv

Proximity visualization output is generated under:

outputs/proximity/

The event information includes fields such as:

worker_id
machinery_id
distance_pixels
safety_zone_margin
confirmation_frames
event

Example:

Worker ID 23
Equipment ID 4
Distance / zone condition satisfied
       ↓
UNSAFE PROXIMITY
Production Consideration

The current implementation is based on image-space geometry.

For production safety distances expressed in metres, calibrated scene geometry, depth information, or a 3D perception system should be used.

The safety threshold should also be configured according to site-specific safety requirements.

❤️ Camera / Stream Health Monitoring

The application includes a dedicated Camera Health Monitor.

The monitor provides visibility into the health of the input video/camera stream during processing.

Typical health information includes:

Stream connected
Input FPS
Frame availability
Last received frame
Dropped / failed frame conditions

For a multi-camera production system, the same monitoring concept can be extended to each RTSP stream independently.

A disconnected camera should not stop processing of unrelated camera streams.

⚙️ Application Health Monitoring

The project includes an Application Monitor for measuring the health of the processing pipeline.

The monitor tracks application-level information such as:

Frames processed
Processing errors
Processing FPS
Frame processing latency
Application runtime

This provides visibility into the complete processing pipeline rather than only model inference.

Conceptually:

Frame Read
   ↓
Detection
   ↓
Tracking
   ↓
PPE Rules
   ↓
Proximity Rules
   ↓
Alert / Reporting
   ↓
Frame Output

Monitoring the end-to-end path provides a more realistic view of application performance.

🖥️ GPU Monitoring

The project includes a GPU Monitor component for collecting GPU-related telemetry where supported.

For NVIDIA GPU environments, the monitoring layer can collect metrics such as:

GPU utilization
GPU memory usage
GPU temperature

The current development environment uses an Intel GPU, so NVIDIA-specific NVML telemetry is not available on that machine.

The monitoring component therefore reports unavailable NVIDIA telemetry rather than treating unavailable data as valid measurements.

For NVIDIA production deployments, including Jetson or discrete NVIDIA GPU environments, platform-specific telemetry can be used.

For Intel GPU deployment, Intel-specific telemetry should be used when hardware-level GPU monitoring is required.

📝 Application Logging

The application captures console output into timestamped log files.

Logs provide operational information such as:

Application startup
Video information
Component initialization
Processing errors
Monitoring information
Application completion

Logs are stored under:

logs/

Logging is useful for:

Debugging
Failure analysis
Performance investigation
Production diagnostics
Deployment verification
---

# 📊 CSV Reporting

The system generates structured CSV reports for downstream analysis.

The PPE report contains fields such as:

```text
frame
worker_id
helmet
vest
mask
status
```

Example:

```text
frame,worker_id,helmet,vest,mask,status
1,1,False,False,False,MONITORING
2,1,True,False,False,NO SAFETY VEST
3,1,True,True,True,SAFE
```

The PPE report is generated under:

```text
reports/video_1_report.csv
```

Worker counting is stored separately:

```text
reports/task1_worker_count.csv
```

CSV output allows the video analytics results to be consumed by:

* Python
* Pandas
* Excel
* BI dashboards
* Database pipelines
* Safety reporting systems

---

# 🎥 Annotated Output Video

The application generates an annotated output video containing visual information from the detection and tracking pipeline.

The output can display:

* Worker bounding boxes
* Worker IDs
* PPE information
* Violation status
* Tracking information

Current example:

```text
data/output_videos/ocsort_output_3.mp4
```

The annotated video provides a convenient way to validate the complete computer vision pipeline.

---

# 🏭 Production / Scalable System Design

The current project is a single-camera technical assessment prototype.

For production deployment, the architecture can be extended to support multiple RTSP cameras.

A scalable architecture can be designed as:

```text
                  ┌──────────────────────┐
Camera 1 ────────►│                      │
Camera 2 ────────►│  Stream Ingestion    │
Camera 3 ────────►│                      │
   ...             └──────────┬───────────┘
Camera 100 ───────►           │
                              ▼
                    ┌──────────────────┐
                    │ Stream Manager   │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ Frame Sampling   │
                    │ / Preprocessing  │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ GPU Inference    │
                    │ YOLO / TensorRT  │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ Multi-Object     │
                    │ Tracking         │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ PPE Association  │
                    │ + Rules Engine   │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ Event Processing │
                    └───────┬───┬──────┘
                            │   │
                ┌───────────┘   └────────────┐
                ▼                            ▼
        ┌───────────────┐            ┌──────────────┐
        │ Alert Service │            │ Event Storage │
        └───────┬───────┘            └──────────────┘
                │
                ▼
        Email / Dashboard /
        Notification System
```

---

# 📈 Scalability – 100 Cameras

The assessment requires consideration of approximately:

```text
100 cameras
1920 × 1080 resolution
15 FPS
24/7 operation
Alert latency < 5 seconds
```

Processing every camera frame independently at full resolution can be computationally expensive.

The production design therefore separates:

* Stream ingestion
* Frame sampling
* GPU inference
* Tracking
* Event processing
* Alerting
* Storage

The system can use frame sampling when continuous full-frame inference is unnecessary.

For example:

```text
Camera stream
     │
     ▼
15 FPS input
     │
     ▼
Frame sampling
     │
     ├── 5 FPS → AI inference
     │
     └── remaining frames → discarded / used for stream continuity
```

The exact sampling rate should be determined through production benchmarking and required detection latency.

---

# ⚡ Batch Inference

Batch inference can improve GPU utilization when multiple camera streams are processed by the same inference service.

Instead of:

```text
Camera 1 → Inference
Camera 2 → Inference
Camera 3 → Inference
```

the inference service can construct a batch:

```text
Frame Camera 1 ─┐
Frame Camera 2 ─┤
Frame Camera 3 ─┼──► GPU Batch Inference
Frame Camera 4 ─┤
Frame Camera N ─┘
```

Batch size should be selected based on:

* GPU memory
* Model size
* Input resolution
* Number of active streams
* Required latency
* Throughput requirements

For real-time safety alerts, excessively large batches should be avoided because they can increase processing latency.

---

# 🧠 Model Selection

The current implementation uses a YOLO-based object detection model.

The model was selected because the application requires:

* Real-time detection
* Multiple object classes
* Worker detection
* PPE detection
* Bounding boxes
* High inference throughput

For production deployment, model selection should consider:

| Factor     | Consideration                   |
| ---------- | ------------------------------- |
| Accuracy   | PPE detection accuracy          |
| FPS        | Real-time processing capability |
| Latency    | Alert response time             |
| Model size | Deployment footprint            |
| GPU memory | Number of simultaneous streams  |
| Resolution | 1080p camera input              |
| Robustness | Lighting and occlusion          |
| Deployment | TensorRT / ONNX / OpenVINO      |

The final production model should be selected after benchmarking on representative construction-site data.

---

# 🚀 TensorRT Optimization

For NVIDIA GPU deployment, the trained YOLO model can be exported to TensorRT.

Typical optimization flow:

```text
YOLO PyTorch Model
        │
        ▼
      ONNX
        │
        ▼
TensorRT Engine
        │
        ├── FP32
        ├── FP16
        └── INT8
```

## FP16

FP16 can reduce memory usage and improve inference throughput on supported NVIDIA GPUs while maintaining close to FP32 accuracy.

## INT8

INT8 can provide further inference acceleration and lower memory consumption.

However, INT8 generally requires calibration data and should be validated carefully because quantization can affect PPE detection accuracy.

The production pipeline should compare:

```text
FP32 vs FP16 vs INT8
```

using:

* mAP
* Precision
* Recall
* FPS
* Latency
* GPU utilization
* Memory utilization

---

# 🧩 Jetson AGX Orin Deployment

The architecture can also target an edge deployment using:

**NVIDIA Jetson AGX Orin**

A possible edge architecture is:

```text
RTSP Camera
     │
     ▼
Jetson AGX Orin
     │
     ├── Video Decode
     ├── Preprocessing
     ├── TensorRT Inference
     ├── Tracking
     ├── PPE Rules
     ├── Event Processing
     └── Local Alert Generation
```

Advantages of edge deployment include:

* Reduced network bandwidth
* Lower dependency on cloud connectivity
* Local processing
* Faster event detection
* Better privacy control
* Ability to continue operating during temporary network outages

---

# ⏱️ Alert Latency Target

The production architecture targets an alert latency of less than approximately:

```text
5 seconds
```

The complete latency includes:

```text
Camera
  ↓
Frame Capture
  ↓
Frame Queue
  ↓
Inference
  ↓
Tracking
  ↓
PPE Association
  ↓
Temporal Confirmation
  ↓
Event Generation
  ↓
Screenshot
  ↓
Notification
```

Latency should be measured end-to-end rather than only measuring model inference time.

---

# 📡 Stream Management

For a multi-camera system, each camera should be treated as an independent stream.

A stream manager should monitor:

* RTSP connection status
* Frame arrival rate
* FPS
* Decode errors
* Queue size
* Last received frame timestamp
* GPU processing latency

A disconnected camera should not stop processing of other cameras.

Conceptually:

```text
Camera 1 ──► Stream Worker 1
Camera 2 ──► Stream Worker 2
Camera 3 ──► Stream Worker 3
...
Camera N ──► Stream Worker N
```

A centralized monitoring layer can report the health of all streams.

---

# ❤️ System Health Monitoring

A production system should monitor:

### Camera Metrics

```text
Stream connected/disconnected
Input FPS
Dropped frames
Last frame timestamp
```

### AI Metrics

```text
Inference FPS
Inference latency
Detection count
Tracking count
GPU utilization
GPU memory
```

### Application Metrics

```text
Violation events
Email delivery status
Screenshot generation
CSV/database write status
Queue size
Processing errors
```

These metrics can be integrated with monitoring systems such as Prometheus/Grafana or an equivalent enterprise monitoring platform.

---

# 🔄 Failure Recovery

The system should continue operating even when individual components fail.

Examples:

### Camera failure

```text
RTSP disconnected
      ↓
Retry connection
      ↓
Reconnect
      ↓
Resume processing
```

### Model failure

The inference worker should report the error and restart or reload the model without bringing down unrelated camera streams.

### Email failure

An email delivery failure should be logged without stopping video processing.

### Storage failure

Events should be buffered or logged so that transient storage failures do not immediately terminate the pipeline.

---

# 🧰 Technologies Used

## Programming

* Python
* OpenCV

## Deep Learning

* YOLO
* PyTorch
* Ultralytics

## Object Tracking

* TrackTrack

## Computer Vision

* Bounding-box analysis
* IoU
* Center-distance association
* Spatial PPE association
* Temporal state tracking

## Reporting

* CSV
* Pandas-compatible output

## Alerting

* SMTP
* Gmail App Password
* Email attachments

## Deployment Concepts

* Docker
* NVIDIA GPU
* TensorRT
* FP16
* INT8
* Jetson AGX Orin
* Multi-camera RTSP architecture

---

# 📁 Project Structure

```text
PPE_Detection/
│
├── README.md
│
├── src/
│   ├── main.py
│   ├── config.py
│   ├── detector.py
│   ├── detection.py
│   ├── ppe_rules.py
│   ├── ppe_state.py
│   ├── csv_logger.py
│   ├── worker_count_logger.py
│   ├── alert_manager.py
│   └── visualizer.py
│
├── models/
│   └── best.pt
│
├── data/
│   ├── input_videos/
│   │   └── ppe_monitoring.mp4
│   │
│   └── output_videos/
│
├── alerts/
│
└── reports/
```

---

# 📦 Module Responsibilities

## `main.py`

Application entry point.

Responsible for connecting:

* Video reader
* Detector
* PPE rules
* PPE state tracker
* CSV logger
* Worker count logger
* Alert manager
* Visualizer

Run using:

```powershell
python src/main.py
```

---

## `detector.py`

Responsible for:

* Loading YOLO model
* Running object detection
* Running tracking
* Returning structured detection objects

---

## `detection.py`

Defines the internal detection data structure containing information such as:

```text
class_id
class_name
confidence
bbox
track_id
```

---

## `ppe_rules.py`

Responsible for:

* Worker/PPE separation
* PPE-to-worker association
* Head-region evaluation
* Torso-region evaluation
* PPE status evaluation

---

## `ppe_state.py`

Responsible for:

* Worker identity association
* Temporal PPE history
* Violation confirmation
* Stable worker IDs
* Missing-frame handling

---

## `csv_logger.py`

Responsible for PPE state reporting.

Output:

```text
reports/video_1_report.csv
```

---

## `worker_count_logger.py`

Responsible for Task 1 worker-count reporting.

Output:

```text
reports/task1_worker_count.csv
```

---

## `alert_manager.py`

Responsible for:

* Violation alerts
* Screenshot generation
* Email notifications
* Alert cooldown

---

## `visualizer.py`

Responsible for rendering the detection and tracking information on the output video.

---

# ⚙️ Installation

Create and activate the Python environment.

Example:

```powershell
conda create -n difinity python=3.11
conda activate difinity
```

Install the required dependencies according to the project environment.

For example:

```powershell
pip install ultralytics
pip install opencv-python
```

Verify the installation:

```powershell
python -c "import ultralytics; print(ultralytics.__version__)"
```

---

# 🧠 Model Weights

Place the trained YOLO model at:

```text
models/best.pt
```

The model should contain the PPE classes required by the application.

The expected classes are:

```text
Person
Hardhat
NO-Hardhat
Safety Vest
NO-Safety Vest
Mask
NO-Mask
```

The model weights should not be committed to a public Git repository.

---

# 🎥 Input Video

Place the input video under:

```text
data/input_videos/
```

Current example:

```text
data/input_videos/ppe_monitoring.mp4
```

The application reads the video and processes it frame by frame.

For production, the video reader can be replaced or extended with an RTSP stream reader.

---

# 📧 Email Configuration

Email credentials should be provided through environment variables.

For PowerShell:

```powershell
$env:PPE_SENDER_EMAIL="your_sender@gmail.com"
$env:PPE_EMAIL_PASSWORD="your_google_app_password"
$env:PPE_SUPERVISOR_EMAIL="supervisor@company.com"
```

Verify:

```powershell
echo $env:PPE_SENDER_EMAIL
echo $env:PPE_SUPERVISOR_EMAIL
```

The application uses:

```text
SMTP Server : smtp.gmail.com
SMTP Port   : 587
Security    : STARTTLS
```

For Gmail, create an App Password and use that value as:

```text
PPE_EMAIL_PASSWORD
```

Do not place passwords directly inside Python source code.

---

# 🔐 Security

The following information should not be committed to source control:

```text
*.pt
*.onnx
*.engine
.env
email passwords
API keys
credentials
private videos
generated alerts
logs
reports containing sensitive information
```

A suitable `.gitignore` should include sensitive files and generated outputs.

Example:

```gitignore
# Model files
*.pt
*.onnx
*.engine

# Environment / credentials
.env

# Generated files
alerts/
logs/
reports/
data/output_videos/

# Python
__pycache__/
*.pyc
```

---

# ▶️ Running the Application

Activate the environment:

```powershell
conda activate difinity
```

Navigate to the project:

```powershell
cd D:\Difinity_Digital\PPE_Detection
```

Run:

```powershell
python src/main.py
```

The application will:

```text
1. Load the YOLO model
2. Open the input video
3. Detect workers and PPE
4. Track workers
5. Associate PPE with workers
6. Maintain temporal PPE state
7. Detect confirmed violations
8. Capture violation screenshots
9. Send email alerts
10. Generate CSV reports
11. Generate annotated output video
```

---

# 📂 Generated Outputs

After execution, the project generates outputs in the following locations.

## Annotated Video

```text
data/output_videos/
```

Example:

```text
ocsort_output_3.mp4
```

## PPE Report

```text
reports/video_1_report.csv
```

## Worker Count Report

```text
reports/task1_worker_count.csv
```

## Violation Screenshots

```text
alerts/
```

These outputs provide evidence that the detection, tracking, PPE monitoring, reporting, and alerting components are operating together.

---

# 📋 Example PPE Report

Example:

```csv
frame,worker_id,helmet,vest,mask,status
1,1,False,False,False,MONITORING
2,1,True,False,False,NO SAFETY VEST
3,1,True,True,False,NO MASK
4,1,True,True,True,SAFE
```

---

# 📋 Example Worker Count Report

Example:

```csv
frame,timestamp_seconds,worker_count
1,0.000,3
2,0.033,3
3,0.067,3
4,0.100,3
```

---

# 🧪 Validation Strategy

The system can be evaluated using the following metrics.

## Detection

```text
Precision
Recall
mAP
Confidence
```

## Tracking

```text
ID consistency
ID switches
Track continuity
Track fragmentation
```

## PPE Classification

```text
Helmet accuracy
Vest accuracy
Mask accuracy
Violation precision
Violation recall
```

## Real-Time Performance

```text
FPS
Inference latency
End-to-end latency
CPU utilization
GPU utilization
GPU memory
```

---

# 📈 Production Performance Evaluation

Before production deployment, the system should be benchmarked using representative construction-site footage.

Testing should include:

* Daylight
* Low light
* Backlighting
* Motion blur
* Partial occlusion
* Crowded scenes
* Different camera angles
* Different worker distances
* Different PPE colors
* PPE partially hidden by tools or equipment

The benchmark should compare model and deployment configurations using the same evaluation dataset.

---

# 🔮 Future Improvements

Potential improvements include:

### 1. Unsafe Proximity Detection

Add worker-to-heavy-equipment proximity monitoring using calibrated distance estimation.

### 2. Multi-Camera Processing

Extend the architecture to support multiple RTSP streams.

### 3. Edge Deployment

Deploy optimized inference on:

```text
Jetson AGX Orin
```

### 4. TensorRT Optimization

Convert the model to:

```text
ONNX → TensorRT
```

and benchmark:

```text
FP32
FP16
INT8
```

### 5. Improved PPE Association

Improve PPE-to-worker association using:

* Better spatial matching
* Keypoints
* Pose estimation
* Depth information
* Scene calibration

### 6. Better Re-Identification

Introduce a dedicated person Re-ID model for difficult occlusion and re-entry scenarios.

### 7. Dashboard

Create a real-time safety dashboard showing:

```text
Active workers
PPE compliance
Active violations
Camera health
Violation history
```

### 8. Database Integration

Store events in a database instead of relying only on CSV files.

### 9. Centralized Alerting

Integrate:

* Email
* SMS
* Microsoft Teams
* Slack
* Webhooks
* Enterprise notification systems

### 10. Monitoring

Add infrastructure and application monitoring for large-scale deployments.

---

# 🎓 Learning Outcomes

This project provided practical experience in:

* Real-time object detection
* YOLO-based inference
* Multi-object tracking
* Worker identity association
* PPE detection
* Spatial object association
* Temporal state tracking
* Safety rule implementation
* Event-driven alerting
* Screenshot evidence generation
* CSV reporting
* Video analytics
* Model deployment considerations
* GPU acceleration
* TensorRT optimization concepts
* Edge-AI architecture
* Multi-camera system design

The project also demonstrates the transition from a standalone computer vision model to an end-to-end video analytics application.

---

# ✅ Project Status

| Feature                     | Status                     |
| --------------------------- | -------------------------- |
| Worker Detection            | ✅ Implemented              |
| Worker Counting             | ✅ Implemented              |
| Worker Tracking             | ✅ Implemented              |
| Worker Identity Association | ✅ Implemented              |
| Helmet Detection            | ✅ Implemented              |
| Safety Vest Detection       | ✅ Implemented              |
| Mask Detection              | ✅ Implemented              |
| Temporal PPE State Tracking | ✅ Implemented              |
| Violation Detection         | ✅ Implemented              |
| Violation Screenshots       | ✅ Implemented              |
| Email Alerts                | ✅ Implemented              |
| CSV Reporting               | ✅ Implemented              |
| Annotated Output Video      | ✅ Implemented              |
| Multi-Camera Deployment     | 🔄 Production Design       |
| TensorRT Optimization       | 🔄 Production Optimization |
| Jetson AGX Orin Deployment  | 🔄 Production Design       |

---

# ⚠️ Limitations

The current implementation is a technical assessment prototype based on video input.

Performance can be affected by:

* Camera placement
* Lighting conditions
* Motion blur
* Occlusion
* Worker overlap
* PPE visibility
* Detection model accuracy
* Tracking performance
* Video resolution
* Camera frame rate

Worker identity tracking can still be affected by severe occlusion or long periods where a worker is completely outside the camera view.

PPE association can also be affected when PPE objects are partially visible or when the worker bounding box does not provide sufficient spatial information.

The current implementation should therefore be considered a prototype and should be validated using representative production data before deployment.

---

# 🏢 Production Deployment Considerations

For a production safety monitoring platform, the following areas require additional engineering and validation:

```text
Camera management
RTSP stream reliability
GPU capacity planning
Model optimization
Multi-camera scheduling
Event storage
Alert reliability
System monitoring
Logging
Failure recovery
Security
Data retention
Access control
```

A production deployment should also establish measurable Service Level Objectives for:

```text
Detection latency
Alert latency
Camera availability
Inference availability
Alert delivery success
System uptime
```

---

# 👤 Author

**Balaji**

Senior Computer Vision Engineer
Computer Vision | Deep Learning | Video Analytics | Robotics

Areas of interest:

* Computer Vision
* Object Detection
* Object Tracking
* 3D Perception
* Video Analytics
* Robotics
* Edge AI
* Vision-Language Models

---

# 📌 Disclaimer

This project was developed as a technical computer vision assessment/prototype for demonstrating an end-to-end PPE safety monitoring workflow.

The system is intended for engineering evaluation and demonstration.

Safety-critical production deployment requires additional validation, representative data collection, model benchmarking, system reliability testing, site-specific safety rules, and appropriate human oversight.
