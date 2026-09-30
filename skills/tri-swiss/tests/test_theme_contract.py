from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
THEME = ROOT / "assets/theme.css"
COMPONENTS = ROOT / "references/components.md"


class TriSwissThemeTests(unittest.TestCase):
    def test_highlight_tokens_are_governed_without_shadows(self) -> None:
        css = THEME.read_text(encoding="utf-8")
        self.assertIn("--highlight", css)
        self.assertIn("--highlight-foreground", css)
        self.assertNotIn("box-shadow", css)

    def test_component_reference_documents_tri_part_stripe(self) -> None:
        self.assertIn("Tri-part segment stripe", COMPONENTS.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
