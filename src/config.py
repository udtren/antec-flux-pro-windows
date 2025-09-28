"""
Configuration management for Antec Flux Pro Display.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class Config:
    """Configuration class for the temperature monitor."""

    cpu_device: Optional[str] = "WMI"
    gpu_device: Optional[str] = "auto"
    polling_interval: int = 1000  # milliseconds

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary for TOML serialization."""
        return {
            "cpu_device": self.cpu_device,
            "gpu_device": self.gpu_device,
            "polling_interval": self.polling_interval,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Config":
        """Create config from dictionary loaded from TOML."""
        return cls(
            cpu_device=data.get("cpu_device", "WMI"),
            gpu_device=data.get("gpu_device", "auto"),
            polling_interval=data.get("polling_interval", 1000),
        )
