"""Tests for the content-hash TTS cache (no real API calls: synthesis is stubbed)."""
import json
import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core import tts, tts_cache  # noqa: E402

VOICE = "gemini:TestVoice"


class FakeSynth:
    """Replaces Gemini batch synthesis: writes the line text as fake audio bytes."""

    def __init__(self, fail_on_idx=None):
        self.calls = []
        self.fail_on_idx = fail_on_idx

    def __call__(self, client, items, total, voice_name, style, exhausted, batch_size=5):
        for idx, text, out_mp3 in items:
            if idx == self.fail_on_idx:
                raise RuntimeError("quota exhausted")
            self.calls.append(idx)
            with open(out_mp3, "w", encoding="utf-8") as f:
                f.write(text)


class TestTtsCache(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.script = os.path.join(self.tmp.name, "script.txt")
        self.audio_dir = os.path.join(self.tmp.name, "audio_vi")

    def tearDown(self):
        self.tmp.cleanup()

    def _write_script(self, lines):
        with open(self.script, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    def _run(self, voice=VOICE, force=False, fail_on_idx=None):
        fake = FakeSynth(fail_on_idx)
        with mock.patch.object(tts, "_synthesize_batch_gemini", fake), \
                mock.patch.object(tts, "_create_fast_genai_client", return_value=None):
            tts.generate_audio(self.script, self.audio_dir, voice=voice, force=force)
        return fake.calls

    def _audio_text(self, idx):
        with open(os.path.join(self.audio_dir, f"{idx:02d}_voice.mp3"), encoding="utf-8") as f:
            return f.read()

    def test_first_run_generates_all_then_fully_cached(self):
        self._write_script(["Câu một", "Câu hai", "Câu ba"])
        self.assertEqual(self._run(), [1, 2, 3])
        self.assertEqual(self._run(), [])

    def test_edited_line_only_regenerates_that_line(self):
        self._write_script(["Câu một", "Câu hai", "Câu ba"])
        self._run()
        self._write_script(["Câu một", "Câu hai ĐÃ SỬA", "Câu ba"])
        self.assertEqual(self._run(), [2])
        self.assertEqual(self._audio_text(2), "Câu hai ĐÃ SỬA")

    def test_inserted_line_keeps_audio_aligned_with_text(self):
        self._write_script(["A", "B", "C"])
        self._run()
        self._write_script(["A", "X mới chèn", "B", "C"])
        self._run()
        for idx, text in enumerate(["A", "X mới chèn", "B", "C"], 1):
            self.assertEqual(self._audio_text(idx), text)

    def test_voice_change_regenerates_everything(self):
        self._write_script(["A", "B"])
        self._run()
        self.assertEqual(self._run(voice="gemini:OtherVoice"), [1, 2])
        self.assertEqual(tts_cache.read_cached_voice(self.audio_dir), "gemini:OtherVoice")

    def test_force_regenerates_everything(self):
        self._write_script(["A", "B"])
        self._run()
        self.assertEqual(self._run(force=True), [1, 2])

    def test_legacy_folder_without_manifest_is_adopted_once(self):
        self._write_script(["A", "B"])
        os.makedirs(self.audio_dir)
        for idx in (1, 2):
            with open(os.path.join(self.audio_dir, f"{idx:02d}_voice.mp3"), "w") as f:
                f.write("old")
        self.assertEqual(self._run(), [])
        self.assertTrue(os.path.exists(tts_cache.manifest_path(self.audio_dir)))
        # After adoption, edits are tracked normally
        self._write_script(["A", "B2"])
        self.assertEqual(self._run(), [2])

    def test_failure_midway_keeps_finished_lines_and_drops_stale_audio(self):
        self._write_script(["A", "B", "C"])
        self._run()
        self._write_script(["A2", "B2", "C"])
        with self.assertRaises(RuntimeError):
            self._run(fail_on_idx=2)
        # Line 1 regenerated and recorded; stale line 2 removed so it can't be rendered by mistake
        self.assertEqual(self._audio_text(1), "A2")
        self.assertFalse(os.path.exists(os.path.join(self.audio_dir, "02_voice.mp3")))
        self.assertEqual(self._run(), [2])

    def test_corrupt_manifest_regenerates_instead_of_crashing(self):
        self._write_script(["A"])
        self._run()
        with open(tts_cache.manifest_path(self.audio_dir), "w") as f:
            f.write("{not json")
        self.assertEqual(self._run(), [1])
        with open(tts_cache.manifest_path(self.audio_dir), encoding="utf-8") as f:
            self.assertIn("01", json.load(f)["lines"])

    def test_cache_key_depends_on_text_voice_and_style(self):
        base = tts_cache.line_cache_key("t", "v", "s")
        self.assertEqual(base, tts_cache.line_cache_key("t", "v", "s"))
        self.assertNotEqual(base, tts_cache.line_cache_key("t2", "v", "s"))
        self.assertNotEqual(base, tts_cache.line_cache_key("t", "v2", "s"))
        self.assertNotEqual(base, tts_cache.line_cache_key("t", "v", "s2"))


if __name__ == "__main__":
    unittest.main()
