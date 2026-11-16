import json
import os
import sys
import tempfile
import unittest

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import build_shorts as bs


class TestBuildShorts(unittest.TestCase):
    def test_resolve_claimed_vs_real_range_paths(self):
        for lang in ("vi", "en"):
            paths = bs.resolve_project_paths("claimed_vs_real_range", lang)
            self.assertTrue(os.path.isfile(paths["script_path"]))
            self.assertTrue(os.path.isdir(paths["media_dir"]))
            self.assertTrue(os.path.isdir(paths["audio_dir"]))

    def test_validate_configs_valid_and_out_of_range(self):
        sample = [{
            "id": "short_01_test",
            "main_topic": "PIN XE ĐIỆN: CÔNG BỐ vs THỰC TẾ",
            "badge": "TẬP 1/4 • BẪY PHÒNG LAB",
            "title_line1": "TITLE",
            "title_line2": "SUBTITLE",
            "accent_color": "#D35400",
            "scenes": [1, 2, 3],
            "thumb_scene": 2,
            "thumb_big_text": "BIG\nTEXT",
            "thumb_sub_badge": "BADGE",
            "yt_titles": ["T1 #shorts"],
            "yt_description": "Desc",
            "yt_pinned_comment": "Comment",
            "thumb_desc": "Layout",
            "thumb_prompt": "Prompt --ar 9:16",
        }]
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(sample, f)
            tmp_path = f.name
        try:
            loaded = bs.load_and_validate_configs(tmp_path, total_scenes=30)
            self.assertEqual(len(loaded), 1)
            self.assertEqual(
                bs.format_overlay_badge(loaded[0], 1, 4, "vi"),
                "PIN XE ĐIỆN: CÔNG BỐ VS THỰC TẾ • TẬP 1/4 • BẪY PHÒNG LAB",
            )
            self.assertEqual(
                bs.format_step_label(2, 4, 3, 7, "vi"),
                "Tập 2/4 • Cảnh 3/7",
            )
            with self.assertRaises(ValueError):
                bs.load_and_validate_configs(tmp_path, total_scenes=2)
        finally:
            os.remove(tmp_path)


if __name__ == "__main__":
    unittest.main()
