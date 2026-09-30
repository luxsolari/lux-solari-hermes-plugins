from pathlib import Path
import unittest


ROUTES = {
    "start", "next", "lesson", "challenge", "checkpoint", "progress",
    "drill", "review", "hint", "explain", "stuck", "recap", "status",
    "help", "reset", "phase", "tracks", "switch", "new-track", "exercise",
}
REFERENCE = Path(__file__).resolve().parents[1] / "references/commands.md"


class CodexRouteTests(unittest.TestCase):
    def test_route_reference_covers_all_published_sage_routes(self) -> None:
        text = REFERENCE.read_text(encoding="utf-8")
        for route in ROUTES:
            self.assertIn(f"sage {route}", text)

    def test_three_axes_contract_is_bundled(self) -> None:
        contract = REFERENCE.parent / "three-axes-contract.md"
        self.assertIn("defaults → global → project → session", contract.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
