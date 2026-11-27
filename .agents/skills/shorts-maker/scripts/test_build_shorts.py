import json
import os
import sys
import tempfile
import unittest

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", "..", ".."))
for p in (SCRIPT_DIR, REPO_ROOT):
    if p not in sys.path:
        sys.path.insert(0, p)

import build_shorts as bs
import make_shorts as ms
from core.subtitles import compute_caption_cue_timings, split_short_caption_chunks


class TestBuildShortsV3(unittest.TestCase):
    def test_resolve_claimed_vs_real_range_paths(self):
        for lang in ("vi", "en"):
            paths = bs.resolve_project_paths("claimed_vs_real_range", lang)
            self.assertTrue(os.path.isfile(paths["script_path"]))
            self.assertTrue(os.path.isdir(paths["media_dir"]))
            self.assertFalse(paths["is_short_first"])

    def test_split_short_caption_chunks_and_cue_timings(self):
        line = "Máy lọc RO 10 lõi đắt hơn máy 5 lõi tới 3 triệu đồng — nhưng độ sạch giống hệt 99.9%!"
        chunks = split_short_caption_chunks(line, max_words=4)
        self.assertGreaterEqual(len(chunks), 3)
        joined_pipes = " | ".join(chunks)
        self.assertIn("10 lõi", joined_pipes)
        self.assertIn("5 lõi", joined_pipes)
        self.assertIn("3 triệu", joined_pipes)

        cues = compute_caption_cue_timings(line, duration=5.4, max_words=4)
        self.assertEqual(len(cues), len(chunks))
        self.assertAlmostEqual(cues[0]["start"], 0.0, places=2)
        self.assertAlmostEqual(cues[-1]["end"], 5.4, places=2)
        for i in range(1, len(cues)):
            self.assertGreaterEqual(cues[i]["start"], cues[i - 1]["end"] - 0.001)

    def test_validate_configs_and_strip_legacy_episode_badges(self):
        sample = [{
            "id": "short_01_test",
            "main_topic": "SẠC NHANH 65W GIÁ RẺ",
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
            badge_out = bs.format_overlay_badge(loaded[0], 1, 4, "vi")
            self.assertNotIn("TẬP", badge_out)
            self.assertIn("SẠC NHANH 65W GIÁ RẺ", badge_out)
            self.assertIn("BẪY PHÒNG LAB", badge_out)
            with self.assertRaises(ValueError):
                bs.load_and_validate_configs(tmp_path, total_scenes=2)
        finally:
            os.remove(tmp_path)

    def test_v3_retention_auditor_flags_length_episode_and_spoilers(self):
        configs = [
            {
                "id": "ep1",
                "badge": "TẬP 1/4 • SỰ THẬT",
                "title_line1": "TIÊU ĐỀ",
                "thumb_sub_badge": "NHÃN",
                "scenes": [1, 2, 3, 4, 5, 6, 7, 8],
                "yt_titles": [
                    "Củ sạc 65W giá 150K và 600K: Tốc độ sạc giống hệt nhau 100% không khác gì cả đâu anh em ơi! #shorts"
                ],
            },
            {"id": "ep2", "scenes": [1, 3], "yt_titles": ["Ngắn gọn #shorts"]},
            {"id": "ep3", "scenes": [4, 5], "yt_titles": ["Ngắn gọn #shorts"]},
        ]
        all_lines = [
            "Củ sạc 65W giá 150K báo sạc nhanh nhưng nóng 50°C.",
            "Câu số 2 dài vừa phải.",
            "Câu số 3 dài vừa phải.",
            "Xét về bài toán giá thành pin mật độ cao, nguyên liệu rất đắt.",
            "Câu số 5.",
            "Câu số 6.",
            "Câu số 7.",
            "Câu số 8.",
        ]
        all_media = [
            "01_hook.mp4", "02_clip.mp4", "03_img.jpg", "04_static.jpg",
            "05_static.jpg", "06_static.jpg", "07_static.jpg", "08_static.jpg",
        ]
        warnings = bs.audit_shorts_retention_risks(configs, all_lines, all_media)
        joined = "\n".join(warnings)
        self.assertIn("duplicates opener of 'ep1'", joined)
        self.assertIn("ep3: Opening scene #04 (04_static.jpg) is a STATIC image", joined)
        self.assertIn("opens with academic transition", joined)
        self.assertIn("Too long (8 scenes", joined)
        self.assertIn("contains episode numbering", joined)
        self.assertIn("Title too long", joined)
        self.assertIn("Title spoils the verdict upfront", joined)

    def test_dual_aspect_overlays_hook_and_caption_strips(self):
        words = "Sạc nhanh 65W GaN sau 5 năm tiết kiệm 3 triệu cho pin LFP".split()
        flags = ms._classify_highlight_words(words)
        self.assertTrue(flags[2])   # 65W
        self.assertTrue(flags[3])   # GaN
        self.assertTrue(flags[5])   # 5
        self.assertTrue(flags[6])   # năm
        self.assertTrue(flags[9])   # 3
        self.assertTrue(flags[10])  # triệu
        self.assertTrue(flags[13])  # LFP

        with tempfile.TemporaryDirectory() as tmpdir:
            ov_916 = os.path.join(tmpdir, "ov_916.png")
            rect_916 = ms.create_short_overlay(
                ov_916, "SẠC NHANH GAN", "BẪY SẠC 150K!", "Nướng Phồng Pin Âm Thầm",
                step_label="Tập 1/1 • Cảnh 1/6", accent_hex="#D35400", is_portrait=True,
            )
            self.assertEqual(rect_916, (0, 0, 1080, 1920))

            ov_169 = os.path.join(tmpdir, "ov_169.png")
            rect_169 = ms.create_short_overlay(
                ov_169, "SẠC NHANH GAN", "BẪY SẠC 150K!", "Nướng Phồng Pin Âm Thầm",
                step_label="Tập 1/1 • Cảnh 6/6", accent_hex="#D35400", is_portrait=False, has_related_video=True,
            )
            self.assertEqual(rect_169, (16, 398, 1048, 740))

            hk_png = os.path.join(tmpdir, "hook.png")
            ms.render_hook_banner_png(hk_png, "BẪY SẠC 65W 150K!", "Nướng Phồng Pin", badge_text="TẬP 1/4 • PHẦN CỨNG")
            self.assertTrue(os.path.isfile(hk_png))

            cap_png = os.path.join(tmpdir, "cap.png")
            ms.render_caption_strip_png(cap_png, "tốn gấp 3 triệu cho pin LFP")
            self.assertTrue(os.path.isfile(cap_png))


if __name__ == "__main__":
    unittest.main()
