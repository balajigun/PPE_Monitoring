# Real-Time PPE Safety Monitoring System
## Technical Design Document

**Author:** Balaji  
**Role:** Senior Computer Vision Engineer  
**Project:** Real-Time PPE Safety Monitoring System  
**Version:** 1.0

---

## 1. Executive Summary

This document describes the technical design of a real-time Computer Vision based PPE Safety Monitoring System.

The system is designed to detect workers, track worker identities, monitor PPE compliance, detect safety violations, capture violation evidence, generate alerts, and identify unsafe proximity between workers and heavy equipment.

The current implementation is a single-camera technical assessment prototype using YOLO-based object detection, Track-Track tracking, spatial PPE association, temporal PPE state tracking, proximity detection, CSV reporting, screenshot generation, email alerts, and system health monitoring.

The architecture is designed so that the current single-camera implementation can be extended to support multiple RTSP camera streams and edge deployment.

For production deployment, the architecture can use GPU-accelerated inference, TensorRT optimization, hardware video decoding, stream management, event processing, centralized monitoring, and edge devices such as NVIDIA Jetson AGX Orin.

## 2. System Requirements

The system must support the following safety-monitoring functions:

### 2.1 Worker Detection

Detect all workers visible in the camera stream and record the number of workers with timestamps.

### 2.2 Worker Tracking

Assign tracking identities to workers and maintain identity consistency across consecutive frames.

### 2.3 PPE Compliance

Monitor:

- Helmet
- Safety vest
- Mask

PPE detections must be associated with the correct worker.

### 2.4 Violation Detection

Detect:

- Missing helmet
- Missing safety vest
- Missing mask

Temporal confirmation is used to reduce false violations caused by individual-frame detection errors.

### 2.5 Violation Evidence

Capture a screenshot when a confirmed violation occurs.

### 2.6 Alerting

Send an email notification containing the violation information and evidence.

### 2.7 Unsafe Proximity

Detect when a worker enters the configured safety zone around heavy equipment.

### 2.8 System Monitoring

Monitor:

- Camera health
- Application health
- Processing performance
- GPU telemetry where supported
- Application logs

## 3. Proposed System Architecture

The proposed architecture separates the system into five major layers:

1. Video ingestion
2. AI inference and tracking
3. Safety rule processing
4. Event and alert processing
5. Monitoring and observability

                   ┌─────────────────────┐
                   │   RTSP / Video      │
                   │      Sources        │
                   └──────────┬──────────┘
                              │
                              ▼
                   ┌─────────────────────┐
                   │  Stream Ingestion   │
                   │  / Video Reader     │
                   └──────────┬──────────┘
                              │
                              ▼
                   ┌─────────────────────┐
                   │ Preprocessing /     │
                   │ Frame Sampling      │
                   └──────────┬──────────┘
                              │
                              ▼
                   ┌─────────────────────┐
                   │ YOLO Detection      │
                   │ + GPU Inference     │
                   └──────────┬──────────┘
                              │
                              ▼
                   ┌─────────────────────┐
                   │TrackTrackTracking   │
                   └──────────┬──────────┘
                              │
                    ┌─────────┴──────────┐
                    ▼                    ▼
          ┌──────────────────┐   ┌──────────────────┐
          │ PPE Association  │   │ Proximity        │
          │ + State Tracker  │   │ Detection        │
          └────────┬─────────┘   └────────┬─────────┘
                   │                      │
                   └──────────┬───────────┘
                              ▼
                   ┌─────────────────────┐
                   │ Event Processing    │
                   └──────────┬──────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
         Screenshot         Email          CSV/Event
           Alerts           Alerts          Storage
                             
                   ┌─────────────────────┐
                   │ Monitoring Layer    │
                   │                     │
                   │ Camera Health       │
                   │ Application Health  │
                   │ GPU Monitoring      │
                   │ Logging             │
                   └─────────────────────┘


                   ## 4. Current AI Processing Pipeline

The current prototype uses a YOLO-based object detection model.

The detector identifies:

- Person
- Hardhat
- NO-Hardhat
- Safety Vest
- NO-Safety Vest
- Mask
- NO-Mask
- Machinery

The detections are converted into structured Detection objects.

OC-SORT is used for multi-object tracking.

The resulting worker tracking information is passed to the PPE state tracker and safety-rule processing modules.

## 4. Unsafe Proximity Detection

Unsafe proximity detection is implemented using image-space geometry.

The system identifies:

- Worker bounding boxes
- Machinery bounding boxes

For each worker, the bottom-center point of the worker bounding box is used as an approximation of the worker's ground-contact position.

The machinery bounding box is expanded by a configurable safety margin.

If the worker foot point enters the expanded machinery safety zone for a configurable number of consecutive frames, an unsafe proximity event is generated.

### Processing Flow

Worker Detection
        ↓
Machinery Detection
        ↓
Tracking
        ↓
Worker Foot Point
        ↓
Machinery Safety Zone
        ↓
Spatial Proximity Check
        ↓
Temporal Confirmation
        ↓
Unsafe Proximity Event

## 5. Scalability – 100 Camera Deployment

The production system is expected to support approximately:

- 100 cameras
- 1920 × 1080 resolution
- 15 FPS
- 24/7 operation
- Alert latency below 5 seconds

A single process should not independently perform all operations for all cameras without resource management.

The production architecture therefore separates:

1. Stream ingestion
2. Frame buffering
3. Frame sampling
4. GPU inference
5. Tracking
6. PPE processing
7. Event processing
8. Alerting
9. Monitoring
10. Storage

## 6. GPU Capacity Planning

GPU capacity will be determined through benchmarking rather than assuming a fixed camera-to-GPU ratio.

The benchmark will measure:

- Inference FPS
- End-to-end FPS
- Inference latency
- End-to-end latency
- GPU utilization
- GPU memory
- CPU utilization
- RAM usage
- Dropped frames
- Queue depth

The number of supported streams per GPU will then be determined from the measured throughput and required safety margin.

## 7. Model Optimization

For NVIDIA deployment, the YOLO model can be optimized using:

PyTorch
   ↓
ONNX
   ↓
TensorRT
   ↓
FP16 / INT8

### FP16

FP16 is the initial optimization target because it can provide improved inference throughput and lower memory usage on supported NVIDIA hardware while generally retaining accuracy close to FP32.

### INT8

INT8 can provide additional optimization but requires representative calibration data.

The optimized model must be validated against the original model using:

- mAP
- Precision
- Recall
- FPS
- Latency
- PPE violation accuracy

## 8. Monitoring and Observability

The system contains three main monitoring components.

### Camera Health Monitor

Tracks:

- Stream availability
- Frame arrival
- Input FPS
- Last received frame
- Failed frame conditions

### Application Monitor

Tracks:

- Frames processed
- Processing errors
- Processing FPS
- Frame-processing latency
- Runtime

### GPU Monitor

Collects GPU telemetry where supported.

For NVIDIA environments this can include:

- GPU utilization
- GPU memory
- GPU temperature

The monitoring layer is designed to be platform-aware. NVIDIA-specific NVML telemetry is not available on the current Intel development environment.


## 9. Failure Recovery

### Camera Failure

RTSP disconnect
      ↓
Detect failure
      ↓
Retry connection
      ↓
Reconnect
      ↓
Resume processing

### Inference Failure

The inference component should report the error and attempt model recovery without stopping unrelated camera streams.

### Alert Failure

Email delivery failure should be logged without stopping video processing.

### Storage Failure

Transient storage failures should be logged and events should be buffered where appropriate.

### Application Failure

Application health metrics and logs should provide enough information to diagnose the failure and restart the affected service.


## 10. Jetson AGX Orin Deployment

For edge deployment, the system can be deployed on NVIDIA Jetson AGX Orin.

The proposed pipeline is:

RTSP
 ↓
Hardware Video Decode
 ↓
Preprocessing
 ↓
TensorRT
 ↓
Tracking
 ↓
PPE Rules
 ↓
Proximity Rules
 ↓
Event Processing
 ↓
Local Alerts

## 11. Performance Benchmarking

The complete pipeline should be benchmarked rather than measuring only YOLO inference time.

The benchmark will capture:

| Metric | Description |
|---|---|
| FPS | End-to-end processed frames per second |
| Inference latency | Model inference time |
| End-to-end latency | Complete processing time |
| GPU utilization | GPU workload |
| GPU memory | GPU memory consumption |
| CPU utilization | CPU workload |
| RAM | Application memory usage |
| Dropped frames | Frames not processed |
| Queue depth | Pending frames |
| Alert latency | Event-to-alert time |

## 12. Conclusion

The current system provides an end-to-end PPE safety monitoring pipeline covering worker detection, tracking, PPE compliance, temporal violation confirmation, violation evidence, email alerting, unsafe proximity detection, reporting, and operational monitoring.

The architecture separates video ingestion, AI inference, tracking, safety rules, event processing, alerting, and monitoring.

The current implementation provides a foundation for production expansion.

Future production work includes multi-camera stream orchestration, GPU capacity benchmarking, TensorRT optimization, Jetson AGX Orin deployment, calibrated proximity estimation, centralized event storage, and enterprise monitoring.