#!/usr/bin/env python3
"""Tests for agent-router.py context profile detection."""
import sys
import unittest
from importlib import import_module
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

agent_router = import_module("agent-router")
detect_profile = agent_router.detect_profile


class TestProfileDetection(unittest.TestCase):

    def test_planning_keyword_ja(self):
        self.assertEqual(detect_profile("このAPIの設計を考えて"), "planning")

    def test_planning_keyword_en(self):
        self.assertEqual(detect_profile("design the architecture for this"), "planning")

    def test_debugging_keyword_ja(self):
        self.assertEqual(detect_profile("このバグを直して"), "debugging")

    def test_debugging_keyword_en(self):
        self.assertEqual(detect_profile("fix this error please"), "debugging")

    def test_incident_keyword_ja(self):
        self.assertEqual(detect_profile("本番で障害が発生した"), "incident")

    def test_incident_keyword_en(self):
        self.assertEqual(detect_profile("production incident happening"), "incident")

    def test_default_no_match(self):
        self.assertEqual(detect_profile("ファイルを作成して"), "default")

    def test_override_planning(self):
        self.assertEqual(detect_profile("@planning このバグを直して"), "planning")

    def test_override_debugging(self):
        self.assertEqual(detect_profile("@debugging 設計を考えて"), "debugging")

    def test_override_incident(self):
        self.assertEqual(detect_profile("@incident 確認して"), "incident")

    def test_override_default(self):
        self.assertEqual(detect_profile("@default このバグを直して"), "default")

    def test_strategy_is_planning(self):
        self.assertEqual(detect_profile("strategy for the project"), "planning")

    def test_crash_is_debugging(self):
        self.assertEqual(detect_profile("the app is crashing"), "debugging")

    def test_urgent_is_incident(self):
        self.assertEqual(detect_profile("urgent production issue"), "incident")


if __name__ == "__main__":
    unittest.main()
