"""
CLI entry point — Race Control Comms
"""
import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from .analyzers.repo import RepoAnalyzer
from .catalog.benchmarks import load_benchmark_scores
from .catalog.ollama import detect_uncatalogued, get_pulled_model_details, scan_library
from .hardware.detect import HardwareSpec, Platform, detect_hardware
from .models.registry import MODEL_CATALOG, ModelRegistry
from .reporters.console import ConsoleReporter
from .reporters.json import JSONReporter


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="hannah",
        description="Hannah — F1 Strategy Engineer for Your LLM Garage",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  hannah                          # Analyze current directory, auto-detect hardware
  hannah /path/to/repo            # Analyze specific repository
  hannah --json                   # Machine-readable output for CI/CD
  hannah --gpu vram=16gb --ram 32gb  # Override hardware detection
  hannah --track "development"    # Focus on coding assistant models
        """
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Repository path to analyze (default: current directory)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON instead of formatted console report"
    )
    parser.add_argument(
        "--track",
        choices=["development", "inference", "general"],
        default="development",
        help="Optimization target: coding assistant, local inference, or balanced"
    )
    parser.add_argument(
        "--gpu",
        help="GPU specification (e.g., 'vram=16gb,model=9070xt')"
    )
    parser.add_argument(
        "--ram",
        help="System RAM (e.g., '16gb', '64gb')"
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored output"
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.10.6"
    )
    return parser


def parse_hardware_overrides(gpu: Optional[str], ram: Optional[str]) -> Optional[HardwareSpec]:
    """Parse --gpu and --ram overrides into HardwareSpec."""
    if not gpu and not ram:
        return None
    
    vram_gb = None
    gpu_model = None
    
    if gpu:
        for part in gpu.split(","):
            if part.startswith("vram="):
                vram_str = part.split("=")[1].lower().replace("gb", "")
                vram_gb = int(vram_str)
            elif part.startswith("model="):
                gpu_model = part.split("=")[1]
    
    ram_gb = None
    if ram:
        ram_gb = int(ram.lower().replace("gb", ""))
    
    return HardwareSpec(
        platform=Platform.MANUAL,
        gpu_vram_gb=vram_gb,
        gpu_model=gpu_model,
        system_ram_gb=ram_gb,
        notes=["Manual hardware override"],
    )


def main(argv: Optional[list] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    
    repo_path = Path(args.path).resolve()
    if not repo_path.exists():
        print(f"❌ Path does not exist: {repo_path}", file=sys.stderr)
        return 1
    
    # Detect hardware
    override = parse_hardware_overrides(args.gpu, args.ram)
    hardware = detect_hardware(override)
    
    # Analyze repository
    analyzer = RepoAnalyzer()
    repo_profile = analyzer.analyze(repo_path)
    
    # Detect locally pulled models (silent empty dict if Ollama not running)
    pulled_details = get_pulled_model_details()
    pulled = set(pulled_details.keys())

    # Discover uncatalogued local models and scan Ollama library (both best-effort)
    catalog_names = {c.name for c in MODEL_CATALOG}
    uncatalogued = detect_uncatalogued(pulled_details, catalog_names)
    vram_budget = hardware.gpu_vram_gb or hardware.system_ram_gb or 8
    library_cands = scan_library(vram_budget)

    # Fetch benchmark scores for catalog models (cached 7 days, silent on network error)
    hf_ids = [c.hf_model_id for c in MODEL_CATALOG if c.hf_model_id]
    benchmark_scores = load_benchmark_scores(hf_ids)

    # Get model recommendations (curated podium + dynamic discoveries)
    registry = ModelRegistry()
    result = registry.recommend(
        repo_profile=repo_profile,
        hardware=hardware,
        track=args.track,
        pulled_models=pulled,
        dynamic_candidates=uncatalogued + library_cands,
        benchmark_scores=benchmark_scores,
    )

    # Report
    if args.json:
        reporter = JSONReporter()
    else:
        reporter = ConsoleReporter(color=not args.no_color)

    reporter.report(repo_profile, hardware, result.podium, args.track, result.discoveries)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
