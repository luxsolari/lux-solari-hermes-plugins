"""Console reporter — Race Control radio in your terminal.

Pure stdlib. ANSI colors are optional and auto-disabled when not a TTY.
"""

from __future__ import annotations

import sys
from typing import Any, Optional

from .notes import race_notes as _race_notes_shared

RULE = "═" * 55
DASH = "─" * 55
PODIUM = {1: "🥇 P1", 2: "🥈 P2", 3: "🥉 P3"}


class ConsoleReporter:
    def __init__(self, color: bool = True) -> None:
        self.color = color and sys.stdout.isatty()

    def _c(self, text: str, code: str) -> str:
        if not self.color:
            return text
        return f"\033[{code}m{text}\033[0m"

    def report(
        self,
        repo: Any,
        hardware: Any,
        recommendations: list,
        track: str,
        discoveries: Optional[list] = None,
    ) -> None:
        bold = lambda t: self._c(t, "1")
        dim = lambda t: self._c(t, "2")

        print(bold("🏁 HANNAH RACE CONTROL — REPOSITORY ANALYSIS COMPLETE"))
        print(RULE)
        print(f"📊 Circuit: {bold(repo.name)}")
        print(f"🏎️  Chassis: {self._chassis(repo)}")
        if repo.frameworks:
            print(f"🔩 Spec: {', '.join(repo.frameworks)}")
        tokens_k = repo.estimated_tokens / 1000
        print(f"⛽ Fuel Load: ~{tokens_k:.0f}K tokens"
              f" ({repo.fuel_label} — {repo.fuel_note})")
        print(f"🔧 Tyre Compound: {bold(repo.compound)} "
              f"(complexity {repo.complexity_score}/10, "
              f"~{repo.total_lines:,} lines / {repo.code_files} files)")
        print()

        print(f"💻 Garage: {bold(hardware.summary())}")
        if hardware.unified_memory:
            print(dim("   Unified memory — RAM doubles as the VRAM pool"))
        print(f"   Quant ceiling: {hardware.max_recommended_quant} · "
              f"32B-class viable: {'yes' if hardware.can_run_32b else 'no (red flag)'}")
        for note in hardware.notes:
            print(dim(f"   · {note}"))
        print()

        print(bold(f"🏆 PODIUM RECOMMENDATIONS  ({track} track)"))
        print(RULE)
        if not recommendations:
            print("⚠️  No models cleared scrutineering for this hardware. Pass --gpu/--ram to override.")
        for rec in recommendations:
            m = rec.model
            head = PODIUM.get(rec.rank, f"   P{rec.rank}")
            tag = f" [{rec.tag}]" if rec.tag else ""
            status = "✅ " if m.pulled else "⬇️  "
            print(f"{head} — {status}{bold(m.name)} ({m.size_gb:.1f} GB, "
                  f"{m.context_k // 1000}K ctx){tag}")
            print(dim(f"     {rec.why}"))
        print()

        if discoveries:
            print()
            print(bold("🔍 GARAGE DISCOVERIES  (not in curated catalog)"))
            print(DASH)
            for d in discoveries:
                status = "✅ " if d.pulled else "⬇️  "
                ctx = f"{d.context_k // 1000}K ctx" if d.context_k else "ctx unknown"
                size = f"{d.size_gb:.1f} GB" if d.size_gb else "size unknown"
                print(f"{status}{bold(d.name)} ({size}, {ctx}) [{d.tag}]")
                if d.source == "community":
                    print(dim("     Detected locally. No benchmark data — evaluate on your own."))
                else:
                    print(dim("     From Ollama library (estimated size). Pull to evaluate."))
            print()

        print(bold("📋 RACE NOTES"))
        for note in _race_notes_shared(repo, hardware):
            print(f"- {note}")
        print(RULE)
        print(dim('"Data is clean. Go win the championship."'))

    def _chassis(self, repo: Any) -> str:
        if not repo.languages:
            return "unknown"
        top = sorted(repo.languages.items(), key=lambda x: -x[1])[:3]
        return " + ".join(lang for lang, _ in top)
