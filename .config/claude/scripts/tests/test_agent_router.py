#!/usr/bin/env python3
"""Tests for agent-router.py keyword/multimodal routing detection."""

import sys
import unittest
from importlib import import_module
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "policy"))

agent_router = import_module("agent-router")
detect_multimodal = agent_router.detect_multimodal
match_keywords = agent_router.match_keywords
match_keywords_regex = agent_router.match_keywords_regex


class TestDetectMultimodal(unittest.TestCase):
    def test_detects_pdf(self):
        self.assertIn("pdf", detect_multimodal("この report.pdf を読んで"))

    def test_detects_image(self):
        self.assertIn("png", detect_multimodal("screenshot.png を確認"))

    def test_detects_video_and_audio(self):
        exts = detect_multimodal("clip.mp4 and track.mp3")
        self.assertIn("mp4", exts)
        self.assertIn("mp3", exts)

    def test_case_insensitive(self):
        # 大文字拡張子も検出される (返り値はマッチした元の表記を保持)
        self.assertIn("PDF", detect_multimodal("DOC.PDF"))

    def test_deduplicates(self):
        self.assertEqual(detect_multimodal("a.pdf b.pdf"), ["pdf"])

    def test_no_match_plain_text(self):
        self.assertEqual(detect_multimodal("ただのテキストです"), [])

    def test_word_boundary_rejects_embedded(self):
        # 拡張子の直後に英数字が続く場合はマッチしない (lookahead)
        self.assertEqual(detect_multimodal("notapdfx"), [])


class TestMatchKeywords(unittest.TestCase):
    def test_matches_japanese_keyword(self):
        matched = match_keywords(
            "このAPIの設計を考えて", agent_router.CODEX_KEYWORDS_JA
        )
        self.assertIn("設計", matched)

    def test_matches_english_keyword(self):
        matched = match_keywords(
            "design the architecture", agent_router.CODEX_KEYWORDS_EN
        )
        self.assertIn("design", matched)

    def test_english_case_insensitive(self):
        matched = match_keywords("DEBUG this", agent_router.CODEX_KEYWORDS_EN)
        self.assertIn("debug", matched)

    def test_gemini_research_keyword(self):
        matched = match_keywords("リサーチして", agent_router.GEMINI_KEYWORDS_JA)
        self.assertIn("リサーチ", matched)

    def test_no_match_returns_empty(self):
        self.assertEqual(
            match_keywords("hello world", agent_router.CODEX_KEYWORDS_JA), []
        )


class TestMatchKeywordsRegex(unittest.TestCase):
    def test_scheduled_pattern(self):
        matched = match_keywords_regex("明日やって", agent_router.SCHEDULED_KEYWORDS)
        self.assertTrue(matched)

    def test_followup_optional_separator(self):
        # "follow.?up" は follow-up / followup 両方にマッチ
        self.assertTrue(
            match_keywords_regex("please follow-up", agent_router.SCHEDULED_KEYWORDS)
        )
        self.assertTrue(
            match_keywords_regex("followup later", agent_router.SCHEDULED_KEYWORDS)
        )

    def test_async_pattern(self):
        matched = match_keywords_regex(
            "バックグラウンドで実行", agent_router.ASYNC_KEYWORDS
        )
        self.assertTrue(matched)

    def test_regex_case_insensitive(self):
        self.assertTrue(
            match_keywords_regex("PARALLEL run", agent_router.ASYNC_KEYWORDS)
        )

    def test_no_match_returns_empty(self):
        self.assertEqual(
            match_keywords_regex("普通の依頼", agent_router.SCHEDULED_KEYWORDS), []
        )


if __name__ == "__main__":
    unittest.main()
