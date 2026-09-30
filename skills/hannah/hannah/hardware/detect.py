"""Hardware detection — pit garage telemetry.

Single source of truth for hardware specs. Pure stdlib, no third-party deps,
so the engine runs in any environment (Claude Code, Codex, plain terminal).
"""

from __future__ import annotations

import platform
import re
import subprocess
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Vendor(str, Enum):
    APPLE = "apple"
    NVIDIA = "nvidia"
    AMD = "amd"
    INTEL = "intel"
    UNKNOWN = "unknown"


class Platform(str, Enum):
    MACOS = "darwin"
    LINUX = "linux"
    WINDOWS = "win32"
    MANUAL = "manual"
    UNKNOWN = "unknown"


# Known AMD discrete GPUs → VRAM (GB). Used when rocm-smi is unavailable.
AMD_VRAM_MAP = {
    "9070XT": 16, "9070": 16,
    "7900XTX": 24, "7900XT": 20, "7900GRE": 16,
    "7800XT": 16, "7700XT": 12, "7600": 8,
}


@dataclass
class HardwareSpec:
    platform: Platform = Platform.UNKNOWN
    cpu_model: Optional[str] = None
    cpu_cores: Optional[int] = None
    system_ram_gb: Optional[int] = None
    gpu_vendor: Vendor = Vendor.UNKNOWN
    gpu_model: Optional[str] = None
    gpu_vram_gb: Optional[int] = None
    gpu_backend: str = "auto"  # mlx, rocm, cuda, cpu
    gpu_count: int = 1         # number of discrete GPUs detected
    notes: list[str] = field(default_factory=list)

    @property
    def unified_memory(self) -> bool:
        return self.platform == Platform.MACOS

    @property
    def can_run_32b(self) -> bool:
        vram = self.gpu_vram_gb or 0
        ram = self.system_ram_gb or 0
        return vram >= 16 or ram >= 32

    @property
    def max_recommended_quant(self) -> str:
        vram = self.gpu_vram_gb or 0
        if vram >= 24:
            return "q6_k"
        if vram >= 16:
            return "q5_k_m"
        if vram >= 8:
            return "q4_k_m"
        return "q3_k_m"

    def summary(self) -> str:
        ram = f"{self.system_ram_gb}GB" if self.system_ram_gb else "?GB"
        if self.unified_memory:
            return f"{self.cpu_model or 'Apple Silicon'} · {ram} unified · {self.gpu_backend}"
        gpu = self.gpu_model or self.gpu_vendor.value
        if self.gpu_count > 1:
            gpu = f"{self.gpu_count}× {gpu}"
        vram = f"{self.gpu_vram_gb}GB VRAM" if self.gpu_vram_gb else "?GB VRAM"
        return f"{gpu} · {vram} · {ram} RAM · {self.gpu_backend}"


def detect_hardware(override: Optional[HardwareSpec] = None) -> HardwareSpec:
    """Detect hardware specs. Use override if provided (manual mode)."""
    if override is not None:
        return override

    system = platform.system().lower()
    if system == "darwin":
        return _detect_macos()
    if system == "linux":
        return _detect_linux()
    if system == "windows":
        return HardwareSpec(platform=Platform.WINDOWS, notes=["Windows detection not implemented; pass --gpu/--ram"])
    return HardwareSpec(platform=Platform.UNKNOWN, notes=["Unknown platform; pass --gpu/--ram"])


def _run(args: list[str], timeout: int = 3) -> Optional[str]:
    try:
        return subprocess.check_output(args, text=True, timeout=timeout, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return None


def _detect_macos() -> HardwareSpec:
    spec = HardwareSpec(platform=Platform.MACOS, gpu_backend="mlx", gpu_vendor=Vendor.APPLE)

    cpu = _run(["sysctl", "-n", "machdep.cpu.brand_string"])
    if cpu:
        spec.cpu_model = cpu

    cores = _run(["sysctl", "-n", "hw.ncpu"])
    if cores and cores.isdigit():
        spec.cpu_cores = int(cores)

    mem = _run(["sysctl", "-n", "hw.memsize"])
    if mem and mem.isdigit():
        spec.system_ram_gb = round(int(mem) / (1024 ** 3))

    # Apple Silicon: unified memory acts as the VRAM pool.
    spec.gpu_vram_gb = spec.system_ram_gb
    spec.notes.append("Apple Silicon unified memory — RAM doubles as VRAM")
    return spec


def _detect_linux() -> HardwareSpec:
    spec = HardwareSpec(platform=Platform.LINUX, gpu_backend="rocm")

    # RAM via /proc/meminfo (no psutil dependency)
    try:
        with open("/proc/meminfo") as fh:
            for line in fh:
                if line.startswith("MemTotal:"):
                    kb = int(line.split()[1])
                    spec.system_ram_gb = round(kb / (1024 ** 2))
                    break
    except Exception:
        pass

    vram, model, vendor, gpu_count = _probe_gpu()
    if vendor:
        spec.gpu_vendor = vendor
    if model:
        spec.gpu_model = model
    if vram is not None:
        spec.gpu_vram_gb = vram
    spec.gpu_count = gpu_count
    if gpu_count > 1:
        spec.notes.append(f"Multi-GPU: {gpu_count} GPUs detected — {vram}GB total VRAM pooled")

    if spec.gpu_vendor == Vendor.NVIDIA:
        spec.gpu_backend = "cuda"
    elif spec.gpu_vendor == Vendor.UNKNOWN:
        spec.gpu_backend = "cpu"

    # No discrete GPU detected → fall back to system RAM as the pool.
    if spec.gpu_vram_gb is None and spec.system_ram_gb:
        spec.gpu_vram_gb = spec.system_ram_gb
        spec.notes.append("No discrete GPU VRAM detected; using system RAM as pool")

    return spec


def _probe_gpu() -> tuple[Optional[int], Optional[str], Optional[Vendor], int]:
    """Probe GPU VRAM/model/vendor/count. Tries NVIDIA, then AMD (rocm-smi, lspci).

    For multi-GPU systems, VRAM is summed across all detected GPUs.
    Returns (total_vram_gb, model_name, vendor, gpu_count).
    """
    # NVIDIA — sum VRAM across all GPUs
    out = _run(["nvidia-smi", "--query-gpu=memory.total,name", "--format=csv,noheader,nounits"])
    if out:
        lines = [ln for ln in out.splitlines() if ln.strip()]
        if lines:
            first_parts = [p.strip() for p in lines[0].split(",")]
            if len(first_parts) >= 2 and first_parts[0].isdigit():
                total_mb = sum(
                    int(ln.split(",")[0].strip())
                    for ln in lines
                    if ln.split(",")[0].strip().isdigit()
                )
                return round(total_mb / 1024), first_parts[1], Vendor.NVIDIA, len(lines)

    # AMD via rocm-smi — sum VRAM across all GPU rows
    out = _run(["rocm-smi", "--showmeminfo", "vram", "--csv"])
    if out:
        lines = out.splitlines()
        data_rows = [ln for ln in lines[1:] if ln.strip()]
        if data_rows:
            try:
                vram_values = [
                    int(row.split(",")[1].strip())
                    for row in data_rows
                    if len(row.split(",")) >= 2 and row.split(",")[1].strip().isdigit()
                ]
                if vram_values:
                    return round(sum(vram_values) / (1024 ** 3)), None, Vendor.AMD, len(vram_values)
            except (ValueError, IndexError):
                pass

    # Fallback: lspci (model name → estimated VRAM from AMD_VRAM_MAP, single GPU only)
    out = _run(["lspci", "-vnn"])
    if out:
        for line in out.splitlines():
            if "VGA" in line or "Display controller" in line:
                if "AMD" in line or "ATI" in line:
                    m = re.search(r"\[AMD/ATI\]\s+(\S+)", line)
                    model = m.group(1) if m else None
                    vram = None
                    if model:
                        for k, v in AMD_VRAM_MAP.items():
                            if k.lower() in model.lower():
                                vram = v
                                break
                    return vram, model, Vendor.AMD, 1
                if "NVIDIA" in line:
                    return None, None, Vendor.NVIDIA, 1

    return None, None, None, 1
