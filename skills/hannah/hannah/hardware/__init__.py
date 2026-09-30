"""Hardware detection — pit garage telemetry.

Re-exports the single source of truth from `detect` so callers can import
from either `hannah.hardware` or `hannah.hardware.detect`.
"""

from .detect import HardwareSpec, Platform, Vendor, detect_hardware

__all__ = ["HardwareSpec", "Platform", "Vendor", "detect_hardware"]
