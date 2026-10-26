from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
THEME = ROOT / "assets/theme.css"
COMPONENTS = ROOT / "references/components.md"


class LuxSwissThemeTests(unittest.TestCase):
    def test_theme_has_required_tokens_without_shadows(self) -> None:
        css = THEME.read_text(encoding="utf-8")
        for token in ("--background", "--foreground", "--primary", "--font-mono", "--font-sans"):
            self.assertIn(token, css)
        self.assertNotIn("box-shadow", css)

    def test_component_catalogue_is_present(self) -> None:
        self.assertIn("Component", COMPONENTS.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
