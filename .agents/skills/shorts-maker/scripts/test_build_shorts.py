import json
import os
import sys
import tempfile
import unittest

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import build_shorts as bs
import make_shorts as ms


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

    def test_audit_shorts_retention_risks_detects_static_and_duplicate_openers(self):
        configs = [
            {"id": "ep1", "scenes": [1, 2]},
            {"id": "ep2", "scenes": [1, 3]},  # Duplicate opener #01
            {"id": "ep3", "scenes": [4, 5]},  # Static .jpg opener + 100% static + academic prefix
        ]
        all_lines = [
            "Hãng hứa năm 2027 bán pin 500 Wh/kg.",
            "Câu số 2.",
            "Câu số 3.",
            "Xét về bài toán giá thành pin mật độ cao, nguyên liệu rất đắt.",
            "Câu số 5.",
        ]
        all_media = [
            "01_hook.mp4",
            "02_clip.mp4",
            "03_img.jpg",
            "04_static.jpg",
            "05_static.jpg",
        ]
        warnings = bs.audit_shorts_retention_risks(configs, all_lines, all_media)
        joined = "\n".join(warnings)
        self.assertIn("duplicates opener of 'ep1'", joined)
        self.assertIn("ep3: Opening scene #04 (04_static.jpg) is a STATIC image", joined)
        self.assertIn("ep3: 0 animated .mp4 clips", joined)
        self.assertIn("opens with academic transition", joined)

    def test_highlight_classification_and_overlay_render(self):
        words = "Sau 5 năm đốt mất 150 triệu cho pin LFP".split()
        flags = ms._classify_highlight_words(words)
        # "5", "năm", "150", "triệu", "LFP" should be highlighted
        self.assertTrue(flags[1])  # 5
        self.assertTrue(flags[2])  # năm
        self.assertTrue(flags[5])  # 150
        self.assertTrue(flags[6])  # triệu
        self.assertTrue(flags[9])  # LFP
        self.assertFalse(flags[0])  # Sau

        with tempfile.TemporaryDirectory() as tmpdir:
            out_vi = os.path.join(tmpdir, "ov_vi.png")
            rect_vi = ms.create_short_overlay(
                out_vi,
                "CHỦ ĐỀ • TẬP 1/4",
                "TIÊU ĐỀ 1",
                "Tiêu đề 2",
                subtitle_text="Sau 5 năm đốt mất 150 triệu cho pin LFP.",
                step_label="Tập 1/4 • Cảnh 6/6",
                accent_hex="#D35400",
            )
            self.assertTrue(os.path.isfile(out_vi))
            self.assertEqual(rect_vi, (16, 505, 1048, 590))


if __name__ == "__main__":
    unittest.main()
