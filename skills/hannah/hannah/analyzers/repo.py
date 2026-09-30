"""Repository analyzer — assess circuit complexity."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


IGNORED_DIRS = {
    "node_modules", "__pycache__", ".git", "venv", ".venv",
    "dist", "build", ".cache", "target", "bin", "obj",
    ".next", ".nuxt", "coverage", ".pytest_cache", ".mypy_cache",
}

CODE_EXTENSIONS = {
    ".py", ".ts", ".tsx", ".js", ".jsx", ".rs", ".go", ".java",
    ".rb", ".swift", ".kt", ".cs", ".cpp", ".c", ".h", ".vue",
    ".svelte", ".json", ".yaml", ".yml", ".toml", ".sql", ".md",
}

LANG_MAP = {
    ".py": "Python", ".ts": "TypeScript", ".tsx": "TypeScript",
    ".js": "JavaScript", ".jsx": "JavaScript", ".rs": "Rust",
    ".go": "Go", ".java": "Java", ".rb": "Ruby", ".swift": "Swift",
    ".kt": "Kotlin", ".cs": "C#", ".cpp": "C++", ".c": "C",
    ".h": "C/Header", ".vue": "Vue", ".svelte": "Svelte",
    ".json": "JSON", ".yaml": "YAML", ".yml": "YAML",
    ".toml": "TOML", ".sql": "SQL", ".md": "Markdown",
}

# Calibrated tokens-per-line rates by language.
# Derived from sampling real files: code fragments into more subword tokens
# than prose due to identifiers, punctuation, and indentation.
TOKENS_PER_LINE: dict[str, float] = {
    "Python": 10.0,
    "TypeScript": 10.0,
    "JavaScript": 10.0,
    "Rust": 11.0,
    "Go": 10.0,
    "Java": 11.0,
    "Ruby": 10.0,
    "Swift": 10.0,
    "Kotlin": 11.0,
    "C#": 11.0,
    "C++": 11.0,
    "C": 11.0,
    "C/Header": 9.0,
    "Vue": 10.0,
    "Svelte": 10.0,
    "SQL": 9.0,
    "JSON": 8.0,
    "YAML": 8.0,
    "TOML": 8.0,
    "Markdown": 6.0,
}
_DEFAULT_TOKENS_PER_LINE = 9.0

# Fuel load labels — how much of a typical model's context window is consumed.
_FUEL_THRESHOLDS = [
    (8_000,   "featherweight", "fits in any context window"),
    (32_000,  "light",         "fits comfortably in 32K+ models"),
    (64_000,  "moderate",      "requires 64K+ context"),
    (128_000, "heavy",         "requires 128K+ context"),
    (256_000, "max load",      "requires 256K+ context"),
    (float("inf"), "overweight", "exceeds 256K — chunked ingestion required"),
]

CONFIG_FILES = {
    "pyproject.toml", "package.json", "Cargo.toml", "go.mod",
    "build.gradle", "pom.xml", ".env.example", "requirements.txt",
    "Dockerfile", "docker-compose.yml", "tsconfig.json",
}

ENTRY_POINTS = {
    "main.py", "app.py", "cli.py", "manage.py",
    "index.ts", "main.ts", "server.py", "main.go", "main.rs",
}

FRAMEWORK_INDICATORS = {
    "fastapi": ["import fastapi", "from fastapi"],
    "react": ["from 'react'", 'from "react"', '"react":', '"react-dom":'],
    "nextjs": ["next.config.", "from 'next/", '"next":'],
    "vue": ["from 'vue'", 'from "vue"', '"vue":'],
    "svelte": ["svelte.config.", '"svelte":', "from 'svelte'"],
    "flask": ["import flask", "from flask import"],
    "django": ["import django", "from django."],
    "pydantic": ["import pydantic", "from pydantic import"],
    "sqlalchemy": ["import sqlalchemy", "from sqlalchemy"],
    "tailwind": ["tailwind.config.", "@tailwind ", '"tailwindcss":'],
    "shadcn": ["shadcn/ui", "components.json"],
    "pywebview": ["import webview", "from webview", "pywebview"],
    "vite": ["vite.config.", '"vite":'],
    "express": ["require('express')", "from 'express'", '"express":'],
    "torch": ["import torch", "from torch"],
}

PROSE_EXTS = {".md"}
SCANNABLE_EXTS = (CODE_EXTENSIONS - PROSE_EXTS) | {".txt", ".cfg", ".ini"}
MAX_SCAN_BYTES = 256 * 1024


@dataclass
class RepoProfile:
    path: Path
    name: str
    languages: dict[str, int] = field(default_factory=dict)       # lang → file count
    lang_lines: dict[str, int] = field(default_factory=dict)       # lang → line count
    total_files: int = 0
    code_files: int = 0
    total_lines: int = 0
    estimated_tokens: int = 0
    fuel_label: str = ""      # e.g. "heavy"
    fuel_note: str = ""       # e.g. "requires 128K+ context"
    config_files: list[str] = field(default_factory=list)
    frameworks: list[str] = field(default_factory=list)
    entry_points: list[str] = field(default_factory=list)
    complexity_score: float = 0.0
    compound: str = "Medium"
    description: str = ""
    notes: list[str] = field(default_factory=list)

    @classmethod
    def from_path(cls, path: Path) -> "RepoProfile":
        profile = cls(path=path, name=path.name or str(path))
        profile._scan()
        profile._estimate_tokens()
        profile._estimate_complexity()
        profile._describe()
        return profile

    def _scan(self) -> None:
        config_seen: set[str] = set()
        for root, dirs, files in os.walk(self.path):
            dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
            for f in files:
                filepath = Path(root) / f
                ext = filepath.suffix.lower()
                self.total_files += 1

                if ext in CODE_EXTENSIONS:
                    self.code_files += 1
                    lang = LANG_MAP.get(ext, ext)
                    self.languages[lang] = self.languages.get(lang, 0) + 1
                    try:
                        text = filepath.read_text(errors="ignore")
                        line_count = len(text.splitlines())
                        self.total_lines += line_count
                        self.lang_lines[lang] = self.lang_lines.get(lang, 0) + line_count
                    except Exception:
                        text = ""
                    if ext not in PROSE_EXTS:
                        self._sniff_frameworks(f, text)
                elif f in CONFIG_FILES or ext in SCANNABLE_EXTS:
                    try:
                        text = filepath.read_text(errors="ignore")
                    except Exception:
                        text = ""
                    self._sniff_frameworks(f, text)

                if f in CONFIG_FILES and f not in config_seen:
                    config_seen.add(f)
                    self.config_files.append(f)
                if f in ENTRY_POINTS:
                    try:
                        rel = str(filepath.relative_to(self.path))
                    except ValueError:
                        rel = f
                    self.entry_points.append(rel)

    def _sniff_frameworks(self, filename: str, text: str) -> None:
        haystack = (filename + "\n" + text[:MAX_SCAN_BYTES]).lower()
        for framework, signals in FRAMEWORK_INDICATORS.items():
            if framework in self.frameworks:
                continue
            if any(sig in haystack for sig in signals):
                self.frameworks.append(framework)

    def _estimate_tokens(self) -> None:
        total = 0
        for lang, lines in self.lang_lines.items():
            rate = TOKENS_PER_LINE.get(lang, _DEFAULT_TOKENS_PER_LINE)
            total += int(lines * rate)
        self.estimated_tokens = total
        for threshold, label, note in _FUEL_THRESHOLDS:
            if total < threshold:
                self.fuel_label = label
                self.fuel_note = note
                break

    def _estimate_complexity(self) -> None:
        score = 0.0
        if self.total_lines < 1000:
            score += 1
        elif self.total_lines < 10_000:
            score += 2
        elif self.total_lines < 50_000:
            score += 4
        elif self.total_lines < 200_000:
            score += 6
        else:
            score += 8
        score += min(2.0, len(self.languages) * 0.3)
        score += min(2.0, len(self.frameworks) * 0.25)
        if len(self.config_files) > 5:
            score += 0.5
        self.complexity_score = min(10.0, round(score, 1))
        self.compound = _compound_for(self.complexity_score)

    def _describe(self) -> None:
        primary = ", ".join(
            f"{lang} ({c} files)"
            for lang, c in sorted(self.languages.items(), key=lambda x: -x[1])[:3]
        ) or "no recognized code files"
        self.description = (
            f"{self.name}: {primary}. ~{self.total_lines:,} lines across "
            f"{self.code_files} code files. Complexity: {self.complexity_score}/10 "
            f"({self.compound}). Frameworks: "
            f"{', '.join(self.frameworks) or 'none detected'}. "
            f"Fuel load: ~{self.estimated_tokens:,} tokens ({self.fuel_label})."
        )


def _compound_for(score: float) -> str:
    if score < 3:
        return "Soft"
    if score < 5:
        return "Medium"
    if score < 7:
        return "Hard"
    return "Intermediate"


class RepoAnalyzer:
    """Thin orchestration wrapper around RepoProfile scanning."""

    def analyze(self, path: Path) -> RepoProfile:
        return RepoProfile.from_path(Path(path))
