"""Tests for Vietnamese caption grouping and TTS pronunciation normalization."""
import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core import tts  # noqa: E402
from core.subtitles import split_short_caption_chunks, split_subtitle_chunks  # noqa: E402
from core.vi_text import group_caption_atoms, normalize_for_tts  # noqa: E402


class TestCompoundCaptions(unittest.TestCase):
    def test_compound_words_stay_together_in_short_captions(self):
        # Real regression from a render: "tùy nhu / cầu đi lại"
        chunks = split_short_caption_chunks("Chọn loại nào tùy nhu cầu đi lại của bạn.")
        joined = " | ".join(chunks)
        self.assertIn("nhu cầu", joined)
        for ch in chunks:
            self.assertFalse(ch.endswith("nhu"), chunks)

    def test_longest_compound_wins(self):
        atoms = group_caption_atoms("mua xe máy điện mới".split())
        self.assertIn("xe máy điện", atoms)

    def test_no_glue_across_punctuation(self):
        atoms = group_caption_atoms("giá xe, máy điện".split())
        self.assertNotIn("xe, máy điện", atoms)

    def test_number_unit_still_grouped(self):
        atoms = group_caption_atoms("tốn 3 triệu mỗi năm".split())
        self.assertIn("3 triệu", atoms)

    def test_long_form_no_single_word_orphan(self):
        chunks = split_subtitle_chunks("Chọn loại nào tùy nhu cầu đi lại của bạn.", max_words=9)
        self.assertTrue(all(len(c.split()) > 1 for c in chunks), chunks)
        self.assertIn("nhu cầu", " | ".join(chunks))

    def test_long_form_chunks_keep_compounds(self):
        text = ("Khi chọn xe máy điện cho nhu cầu đi lại hàng ngày, bạn cần hiểu rõ sự khác biệt "
                "giữa hai loại pin phổ biến hiện nay trên thị trường")
        chunks = split_subtitle_chunks(text, max_words=9)
        self.assertEqual(" ".join(chunks).split(), text.split())  # nothing lost or reordered
        for ch in chunks:
            self.assertFalse(ch.endswith((" nhu", " xe", " xe máy", " khác")), chunks)


class TestPronunciation(unittest.TestCase):
    def test_units_after_numbers(self):
        self.assertEqual(normalize_for_tts("Củ sạc 65W giá 150K"), "Củ sạc 65 oát giá 150 nghìn")
        self.assertEqual(normalize_for_tts("nóng 45°C"), "nóng 45 độ C")
        self.assertEqual(normalize_for_tts("chạy 80 km/h"), "chạy 80 ki lô mét trên giờ")

    def test_longer_unit_wins(self):
        self.assertEqual(normalize_for_tts("pin 3 kWh"), "pin 3 ki lô oát giờ")
        self.assertEqual(normalize_for_tts("pin 5000mAh"), "pin 5000 mi li am pe giờ")

    def test_terms_are_spelled(self):
        self.assertEqual(normalize_for_tts("Pin LFP chuẩn IP67"), "Pin L F P chuẩn I P 67")

    def test_letters_without_numbers_untouched(self):
        self.assertEqual(normalize_for_tts("nhóm A và W cũ"), "nhóm A và W cũ")


class TestTtsUsesSpokenText(unittest.TestCase):
    def test_tts_receives_normalized_text_and_keeps_original_for_subtitles(self):
        with tempfile.TemporaryDirectory() as tmp:
            script = os.path.join(tmp, "script_vi.txt")
            with open(script, "w", encoding="utf-8") as f:
                f.write("Củ sạc 65W giá 150K.\n")
            sent = []

            def fake_batch(client, items, total, voice_name, style, exhausted, batch_size=5):
                for idx, text, out_mp3 in items:
                    sent.append(text)
                    with open(out_mp3, "w", encoding="utf-8") as fo:
                        fo.write(text)

            with mock.patch.object(tts, "_synthesize_batch_gemini", fake_batch), \
                    mock.patch.object(tts, "_create_fast_genai_client", return_value=None):
                items = tts.generate_audio(script, os.path.join(tmp, "audio_vi"), voice="gemini:Test")

        self.assertEqual(sent, ["Củ sạc 65 oát giá 150 nghìn."])
        self.assertEqual(items[0]["text"], "Củ sạc 65W giá 150K.")


if __name__ == "__main__":
    unittest.main()
