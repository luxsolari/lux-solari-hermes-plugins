"""Shared race notes generator — actionable pit-wall advice for every platform."""

from __future__ import annotations

import os
from typing import Any


def race_notes(repo: Any, hardware: Any) -> list[str]:
    notes: list[str] = []

    backend = getattr(hardware, "gpu_backend", "cpu")
    vendor = getattr(hardware, "gpu_vendor", None)
    vendor_val = getattr(vendor, "value", "").lower()
    cpu_cores = getattr(hardware, "cpu_cores", 0) or 0
    plat = str(getattr(hardware, "platform", "")).lower()

    ctx_k = 256 if repo.complexity_score >= 5 else 128
    ctx_val = ctx_k * 1024

    if "darwin" in plat:
        notes += _notes_macos(ctx_val)
    elif "linux" in plat:
        wsl = _is_wsl()
        if wsl and not _wsl_has_systemd():
            notes += _notes_wsl_no_systemd(backend, vendor_val, ctx_val)
        else:
            # Native Linux or WSL2 with systemd — both use systemctl
            notes += _notes_linux_systemd(backend, vendor_val, cpu_cores, ctx_val)
    elif "win" in plat:
        notes += _notes_windows(ctx_val)

    if not hardware.can_run_32b:
        notes.append("Avoid 32B+ models — guaranteed DNF on this VRAM budget")

    if repo.entry_points:
        notes.append(f"Entry points: {', '.join(repo.entry_points[:4])}")

    return notes


# ---------------------------------------------------------------------------
# Platform-specific note builders
# ---------------------------------------------------------------------------

def _notes_macos(ctx_val: int) -> list[str]:
    """macOS — Ollama runs as a launchd user agent."""
    return [
        f"launchctl setenv OLLAMA_FLASH_ATTENTION 1 &&"
        f" launchctl setenv OLLAMA_CONTEXT_LENGTH {ctx_val} &&"
        f" launchctl setenv OLLAMA_KEEP_ALIVE -1",
        "killall Ollama && open -a Ollama  ← restart to apply env changes",
        "Model param (modelfile / API): num_gpu=999  ← offload all layers to Metal",
    ]


def _notes_linux_systemd(backend: str, vendor_val: str, cpu_cores: int, ctx_val: int) -> list[str]:
    """Native Linux or WSL2 with systemd — use systemctl edit drop-in."""
    is_amd = backend == "rocm" or "amd" in vendor_val
    is_nvidia = backend == "cuda" or "nvidia" in vendor_val

    if is_amd or is_nvidia:
        env_block = (
            f'Environment="OLLAMA_FLASH_ATTENTION=1"'
            f' Environment="OLLAMA_CONTEXT_LENGTH={ctx_val}"'
            f' Environment="OLLAMA_KEEP_ALIVE=-1"'
        )
        notes = [
            f"systemctl edit ollama — add under [Service]: {env_block}",
            "sudo systemctl daemon-reload && sudo systemctl restart ollama",
        ]
        if is_amd:
            notes.append(
                "Model param (modelfile / API): num_gpu=999"
                " — OLLAMA_FLASH_ATTENTION=1 requires RDNA3+ (7000/9000 series)"
            )
        else:
            notes.append("Model param (modelfile / API): num_gpu=999")
        return notes

    # CPU-only
    thread_hint = max(1, (cpu_cores or 4) - 2)
    cpu_ctx = ctx_val // 2
    return [
        f'systemctl edit ollama — add under [Service]:'
        f' Environment="OLLAMA_CONTEXT_LENGTH={cpu_ctx}"'
        f' Environment="OLLAMA_NUM_PARALLEL=1"',
        "sudo systemctl daemon-reload && sudo systemctl restart ollama",
        f"Model param: num_gpu=0 num_thread={thread_hint}  ← CPU-only; raise ctx if RAM allows",
    ]


def _notes_wsl_no_systemd(backend: str, vendor_val: str, ctx_val: int) -> list[str]:
    """WSL2 without systemd — env vars in shell profile; GPU may live on Windows host."""
    is_gpu = backend in ("rocm", "cuda") or "amd" in vendor_val or "nvidia" in vendor_val
    notes = [
        f"Add to ~/.bashrc: export OLLAMA_FLASH_ATTENTION=1"
        f" OLLAMA_CONTEXT_LENGTH={ctx_val} OLLAMA_KEEP_ALIVE=-1",
    ]
    if is_gpu:
        notes.append(
            "If Ollama runs on the Windows host (common in WSL2):"
            " export OLLAMA_HOST=host.docker.internal:11434  ← add to ~/.bashrc too"
        )
        notes.append("Model param (modelfile / API): num_gpu=999")
    else:
        notes.append("Model param: num_gpu=0  ← GPU passthrough not configured")
    return notes


def _notes_windows(ctx_val: int) -> list[str]:
    """Windows native — Ollama reads user-level environment variables."""
    ps = "[Environment]::SetEnvironmentVariable"
    return [
        f'PowerShell: {ps}("OLLAMA_FLASH_ATTENTION","1","User")'
        f' ; {ps}("OLLAMA_CONTEXT_LENGTH","{ctx_val}","User")'
        f' ; {ps}("OLLAMA_KEEP_ALIVE","-1","User")',
        "Restart Ollama from the system tray to apply the new env vars",
        "Model param (modelfile / API): num_gpu=999",
    ]


# ---------------------------------------------------------------------------
# Detection helpers
# ---------------------------------------------------------------------------

def _is_wsl() -> bool:
    try:
        with open("/proc/version") as fh:
            return "microsoft" in fh.read().lower()
    except Exception:
        return False


def _wsl_has_systemd() -> bool:
    return os.path.isdir("/run/systemd/private")
