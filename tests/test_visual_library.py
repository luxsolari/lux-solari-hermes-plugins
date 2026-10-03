"""Preserve the complete craft library through the Hermes host adapter."""
import hashlib
import json
from pathlib import Path
import re
import struct
import unittest
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills/lux-visual-systems'


class CraftLibraryTests(unittest.TestCase):
    def test_craft_collection_preserves_every_source_image(self) -> None:
        inventory = json.loads((SKILL / "references/craft-stickers.json").read_text())
        entries = inventory["entries"]
        self.assertEqual(inventory["schema_version"], 1)
        self.assertEqual(inventory["source_image_count"], 57)
        self.assertEqual(len(entries), 57)
        self.assertEqual(len({entry["source_name"] for entry in entries}), 57)
        self.assertEqual(inventory["unique_image_count"], 56)
        self.assertEqual(len({entry["sha256"] for entry in entries}), 56)
        new_paths = set()
        for entry in entries:
            with self.subTest(source=entry["source_name"]):
                path = SKILL / entry["asset"]
                self.assertTrue(path.resolve().is_relative_to(SKILL.resolve()))
                data = path.read_bytes()
                self.assertEqual(hashlib.sha256(data).hexdigest(), entry["sha256"])
                self.assertEqual(len(data), entry["bytes"])
                self.assertEqual(data[:8], b"\x89PNG\r\n\x1a\n")
                self.assertEqual(data[12:16], b"IHDR")
                self.assertEqual(
                    struct.unpack(">II", data[16:24]),
                    (entry["width"], entry["height"]),
                )
                if path.parent.name == "craft-stickers":
                    self.assertEqual(path.name, entry["source_name"])
                    new_paths.add(path)
        self.assertEqual(inventory["added_image_count"], 44)
        self.assertEqual(len(new_paths), 44)
        self.assertEqual(new_paths, set((SKILL / "assets/craft-stickers").glob("*.png")))

    def test_craft_catalogue_links_every_original_for_portable_selection(self) -> None:
        references = SKILL / "references"
        inventory = json.loads((references / "craft-stickers.json").read_text())
        catalogue = (references / "craft-stickers.md").read_text()
        rows = re.findall(r"\| \[([^\]]+)\]\(([^)]+)\) \|", catalogue)
        self.assertEqual(len(rows), 57)
        linked = {name: (references / unquote(link)).resolve() for name, link in rows}
        for entry in inventory["entries"]:
            with self.subTest(source=entry["source_name"]):
                self.assertEqual(
                    linked[entry["source_name"]], (SKILL / entry["asset"]).resolve()
                )
                self.assertIn(entry["description"], catalogue)
                self.assertIn(entry["reference_mode"], {"light", "dark", "multicolor"})
        self.assertEqual(
            {entry["category"] for entry in inventory["entries"]},
            {"canonical", "mixed-craft", "character", "illustration", "photography",
             "photography-card", "film-label", "gaming"},
        )
        skill = (SKILL / "SKILL.md").read_text()
        self.assertIn("references/craft-stickers.md", skill)
        self.assertIn("version: 1.3.0", skill)
        self.assertIn("Hermes `image_generate`", skill)
        self.assertIn("visually inspect", skill)
        self.assertNotIn("/Users/", skill + catalogue + json.dumps(inventory))

