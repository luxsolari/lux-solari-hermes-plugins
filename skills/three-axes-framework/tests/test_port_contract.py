"""Static contract for the conversational port, not native hook tests."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ConversationalPortTests(unittest.TestCase):
    def test_every_integrity_rule_and_mode_duration_survives(self):
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertEqual(set(re.findall(r"\*\*(IR-\d{2}) ", skill)),
                         {f"IR-{i:02d}" for i in range(1, 14)})
        for duration in ("Attempt-bounded", "Single-task", "Topic-bounded", "Single-response"):
            self.assertIn(duration, skill)
        self.assertIn("not** an automatic tool-denial hook", skill)

    def test_presets_match_retained_upstream_command(self):
        source = (ROOT / "references/source-commands/three-axes-mode.md").read_text(encoding="utf-8")
        routes = (ROOT / "references/commands.md").read_text(encoding="utf-8")
        pattern = r"\|\s*(learning|output|production|explore|balanced)\s*\|\s*(low|medium|high)\s*\|\s*(low|medium|high)\s*\|\s*(growth|balanced|output)\s*\|"
        self.assertEqual(set(re.findall(pattern, source)), set(re.findall(pattern, routes)))
        self.assertEqual(len(re.findall(pattern, routes)), 5)
        self.assertNotIn("~/.codex/", routes)
        self.assertIn("not registered slash", routes)

    def test_frontmatter_description_and_porting_warning(self):
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        match = re.search(r'^description: "(.*)"$', skill, re.M)
        assert match is not None
        description = match.group(1)
        self.assertLessEqual(len(description), 60)
        self.assertTrue(description.endswith("."))
        self.assertIn("## Pitfalls", skill)
        self.assertIn("HERMES_HOME", skill)
        self.assertIn("Session overrides stay in conversation", skill)


if __name__ == "__main__":
    unittest.main()
