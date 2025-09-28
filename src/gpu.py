"""
GPU temperature monitoring for Windows.
Supports NVIDIA GPUs via pynvml (Python bindings for NVML).
"""

from typing import Optional
import os


class GPUMonitor:
    """Monitor GPU temperature on Windows systems."""

    def __init__(self, device: Optional[str] = None):
        self.device = device or "auto"
        self.nvidia_gpu = None
        self._initialize()

    def _initialize(self):
        """Initialize GPU monitoring."""
        if self.device == "auto" or self.device == "nvidia":
            self.nvidia_gpu = self._init_nvidia()

    def _init_nvidia(self) -> Optional["NvidiaGPU"]:
        """Initialize NVIDIA GPU monitoring."""
        try:
            import pynvml

            pynvml.nvmlInit()

            device_count = pynvml.nvmlDeviceGetCount()
            if device_count > 0:
                return NvidiaGPU(pynvml)
            else:
                print("No NVIDIA GPUs found")
                return None

        except ImportError:
            print("Warning: pynvml not available. Install with: pip install pynvml")
            return None
        except Exception as e:
            print(f"Warning: Failed to initialize NVIDIA GPU monitoring: {e}")
            return None

    def get_temperature(self) -> Optional[float]:
        """Get current GPU temperature in Celsius."""
        if self.nvidia_gpu:
            return self.nvidia_gpu.get_temperature()

        return None

    def get_info(self) -> str:
        """Get information about the GPU monitoring method."""
        if self.nvidia_gpu:
            return f"GPU monitoring: NVIDIA (pynvml)"

        return "GPU monitoring: No compatible GPU found"


class NvidiaGPU:
    """NVIDIA GPU temperature monitoring using pynvml."""

    def __init__(self, pynvml_module, device_index: int = 0):
        self.pynvml = pynvml_module
        self.device_index = device_index

        try:
            self.handle = self.pynvml.nvmlDeviceGetHandleByIndex(device_index)
            # Get device name for info - handle both bytes and string returns
            name_result = self.pynvml.nvmlDeviceGetName(self.handle)
            if isinstance(name_result, bytes):
                self.name = name_result.decode("utf-8")
            else:
                self.name = str(name_result)
        except Exception as e:
            print(f"Warning: Failed to get NVIDIA GPU handle: {e}")
            self.handle = None
            self.name = "Unknown NVIDIA GPU"

    def get_temperature(self) -> Optional[float]:
        """Get GPU temperature in Celsius."""
        if not self.handle:
            return None

        try:
            # NVML_TEMPERATURE_GPU = 0
            temp = self.pynvml.nvmlDeviceGetTemperature(self.handle, 0)
            return float(temp)
        except Exception as e:
            print(f"Error getting GPU temperature: {e}")
            return None
