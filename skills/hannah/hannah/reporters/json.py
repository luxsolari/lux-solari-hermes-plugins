"""JSON reporter — machine-readable telemetry for CI/CD and agent consumption."""

from __future__ import annotations

import json
from typing import Any, Optional

from .notes import race_notes as _race_notes


class JSONReporter:
    def report(
        self,
        repo: Any,
        hardware: Any,
        recommendations: list,
        track: str,
        discoveries: Optional[list] = None,
    ) -> None:
        print(json.dumps(self.build(repo, hardware, recommendations, track, discoveries), indent=2))

    def build(
        self,
        repo: Any,
        hardware: Any,
        recommendations: list,
        track: str,
        discoveries: Optional[list] = None,
    ) -> dict:
        return {
            "schema": "hannah/analysis@1",
            "track": track,
            "repo": {
                "name": repo.name,
                "path": str(repo.path),
                "languages": repo.languages,
                "total_files": repo.total_files,
                "code_files": repo.code_files,
                "total_lines": repo.total_lines,
                "frameworks": repo.frameworks,
                "config_files": repo.config_files,
                "entry_points": repo.entry_points,
                "complexity_score": repo.complexity_score,
                "compound": repo.compound,
                "description": repo.description,
                "estimated_tokens": repo.estimated_tokens,
                "fuel_label": repo.fuel_label,
                "fuel_note": repo.fuel_note,
            },
            "hardware": {
                "platform": _enum(hardware.platform),
                "cpu_model": hardware.cpu_model,
                "cpu_cores": hardware.cpu_cores,
                "system_ram_gb": hardware.system_ram_gb,
                "gpu_vendor": _enum(hardware.gpu_vendor),
                "gpu_model": hardware.gpu_model,
                "gpu_vram_gb": hardware.gpu_vram_gb,
                "gpu_backend": hardware.gpu_backend,
                "unified_memory": hardware.unified_memory,
                "can_run_32b": hardware.can_run_32b,
                "max_recommended_quant": hardware.max_recommended_quant,
                "notes": hardware.notes,
            },
            "recommendations": [
                {
                    "rank": rec.rank,
                    "name": rec.model.name,
                    "family": rec.model.family,
                    "params_b": rec.model.params_b,
                    "quant": rec.model.quant,
                    "size_gb": rec.model.size_gb,
                    "context_k": rec.model.context_k,
                    "strengths": rec.model.strengths,
                    "mlx": rec.model.mlx,
                    "pulled": rec.model.pulled,
                    "tag": rec.tag,
                    "why": rec.why,
                }
                for rec in recommendations
            ],
            "discoveries": [
                {
                    "name": d.name,
                    "family": d.family,
                    "size_gb": d.size_gb,
                    "context_k": d.context_k,
                    "quant": d.quant,
                    "source": d.source,
                    "pulled": d.pulled,
                    "tag": d.tag,
                }
                for d in (discoveries or [])
            ],
            "race_notes": _race_notes(repo, hardware),
        }


def _enum(value: Any) -> Any:
    return getattr(value, "value", value)
