from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from iat_core.models import CustomPreset
from iat_core.preset_store import CustomPresetStore
from ui.state import parse_words


class CustomPresetTests(unittest.TestCase):
    def test_display_name_preserves_swift_fallbacks(self) -> None:
        self.assertEqual(
            CustomPreset("1", "", "", "", "", "").display_name,
            "未命名",
        )
        self.assertEqual(
            CustomPreset("1", "", "", "", "反对", "").display_name,
            "yy/反对",
        )
        self.assertEqual(
            CustomPreset("1", "", "", "赞同", "", "").display_name,
            "赞同/zz",
        )

    def test_json_round_trip_and_missing_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "presets.json"
            store = CustomPresetStore(path)
            self.assertEqual(store.load(), [])

            presets = [
                CustomPreset(
                    id="fixed",
                    positive_text="好",
                    negative_text="坏",
                    yy_text="喜欢",
                    zz_text="不喜欢",
                    updated_at="2026-06-22T00:00:00+00:00",
                )
            ]
            store.save(presets)
            self.assertEqual(store.load(), presets)
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(payload[0]["positive_text"], "好")

    def test_invalid_json_returns_empty_list(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "presets.json"
            path.write_text("{bad", encoding="utf-8")
            self.assertEqual(CustomPresetStore(path).load(), [])


class ParseWordsTests(unittest.TestCase):
    def test_all_swift_separators(self) -> None:
        self.assertEqual(
            parse_words("甲,乙，丙;丁\n戊 己/庚／辛"),
            ("甲", "乙", "丙", "丁", "戊", "己", "庚", "辛"),
        )


if __name__ == "__main__":
    unittest.main()
