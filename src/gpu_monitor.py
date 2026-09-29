"""
gpu_monitor.py

GPU monitoring for production deployment.

Supports NVIDIA GPUs through NVML when available.

If an NVIDIA GPU is unavailable, monitoring reports
GPU status as NOT_AVAILABLE instead of crashing
the application.
"""

import time


class GPUMonitor:

    def __init__(
        self,
        gpu_index=0
    ):

        self.gpu_index = gpu_index

        self.available = False

        self.nvml = None
        self.handle = None

        self.status = "NOT_AVAILABLE"

        self._initialize()

    # ============================================================
    # INITIALIZE NVML
    # ============================================================

    def _initialize(self):

        try:

            import pynvml

            self.nvml = pynvml

            self.nvml.nvmlInit()

            self.handle = (
                self.nvml.nvmlDeviceGetHandleByIndex(
                    self.gpu_index
                )
            )

            self.available = True

            self.status = "HEALTHY"

        except Exception as e:

            self.available = False

            self.status = "NOT_AVAILABLE"

            print(
                f"[GPU MONITOR] "
                f"NVIDIA GPU monitoring unavailable: "
                f"{e}"
            )

    # ============================================================
    # GET GPU METRICS
    # ============================================================

    def get_metrics(self):

        if not self.available:

            return {
                "status": "NOT_AVAILABLE",
                "gpu_name": "N/A",
                "gpu_utilization_percent": None,
                "memory_used_mb": None,
                "memory_total_mb": None,
                "memory_utilization_percent": None,
                "temperature_c": None,
                "power_watts": None
            }

        try:

            utilization = (
                self.nvml.nvmlDeviceGetUtilizationRates(
                    self.handle
                )
            )

            memory = (
                self.nvml.nvmlDeviceGetMemoryInfo(
                    self.handle
                )
            )

            temperature = (
                self.nvml.nvmlDeviceGetTemperature(
                    self.handle,
                    self.nvml.NVML_TEMPERATURE_GPU
                )
            )

            # Power is returned in milliwatts
            try:

                power_watts = (
                    self.nvml.nvmlDeviceGetPowerUsage(
                        self.handle
                    ) / 1000.0
                )

            except Exception:

                power_watts = None

            name = (
                self.nvml.nvmlDeviceGetName(
                    self.handle
                )
            )

            if isinstance(name, bytes):

                name = name.decode(
                    "utf-8",
                    errors="ignore"
                )

            memory_used_mb = (
                memory.used /
                (1024 * 1024)
            )

            memory_total_mb = (
                memory.total /
                (1024 * 1024)
            )

            memory_utilization = (
                memory.used /
                memory.total
            ) * 100.0

            # GPU health status
            if utilization.gpu >= 98:

                status = "HIGH_UTILIZATION"

            elif temperature >= 85:

                status = "HIGH_TEMPERATURE"

            elif memory_utilization >= 95:

                status = "HIGH_MEMORY"

            else:

                status = "HEALTHY"

            self.status = status

            return {
                "status": status,
                "gpu_name": name,
                "gpu_utilization_percent": round(
                    utilization.gpu,
                    2
                ),
                "memory_used_mb": round(
                    memory_used_mb,
                    2
                ),
                "memory_total_mb": round(
                    memory_total_mb,
                    2
                ),
                "memory_utilization_percent": round(
                    memory_utilization,
                    2
                ),
                "temperature_c": round(
                    temperature,
                    2
                ),
                "power_watts": (
                    round(
                        power_watts,
                        2
                    )
                    if power_watts is not None
                    else None
                )
            }

        except Exception as e:

            self.status = "ERROR"

            return {
                "status": "ERROR",
                "gpu_name": "N/A",
                "gpu_utilization_percent": None,
                "memory_used_mb": None,
                "memory_total_mb": None,
                "memory_utilization_percent": None,
                "temperature_c": None,
                "power_watts": None,
                "error": str(e)
            }

    # ============================================================
    # PRINT GPU STATUS
    # ============================================================

    def print_metrics(self):

        metrics = self.get_metrics()

        print(
            "\n========== GPU MONITOR =========="
        )

        print(
            f"Status             : "
            f"{metrics['status']}"
        )

        print(
            f"GPU                : "
            f"{metrics['gpu_name']}"
        )

        print(
            f"GPU Utilization    : "
            f"{metrics['gpu_utilization_percent']} %"
        )

        print(
            f"Memory Used        : "
            f"{metrics['memory_used_mb']} MB"
        )

        print(
            f"Memory Total       : "
            f"{metrics['memory_total_mb']} MB"
        )

        print(
            f"Memory Utilization : "
            f"{metrics['memory_utilization_percent']} %"
        )

        print(
            f"Temperature        : "
            f"{metrics['temperature_c']} °C"
        )

        print(
            f"Power              : "
            f"{metrics['power_watts']} W"
        )

        print(
            "================================="
        )

    # ============================================================
    # SHUTDOWN
    # ============================================================

    def close(self):

        if self.available and self.nvml is not None:

            try:

                self.nvml.nvmlShutdown()

            except Exception:

                pass

            self.available = False