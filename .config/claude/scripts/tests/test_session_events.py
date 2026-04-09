"""Tests for session_events.py — importance scoring."""

import json
import sys
from pathlib import Path

import pytest

# scripts/lib/ ディレクトリをパスに追加
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

from session_events import (
    BASE_CONFIDENCE,
    RULE_CONFIDENCE,
    _normalize_event,
    compute_importance,
    compute_skill_score,
    emit_event,
    emit_review_feedback,
    emit_review_finding,
    emit_skill_event,
    emit_skill_step,
    flush_session,
    read_pending_findings,
    update_finding_outcome,
)


@pytest.fixture(autouse=True)
def isolate_data_dir(tmp_path, monkeypatch):
    """全テストで AUTOEVOLVE_DATA_DIR を tmpdir に隔離する。"""
    monkeypatch.setenv("AUTOEVOLVE_DATA_DIR", str(tmp_path))
    # ロガーのハンドラをリセット（テスト間で干渉しないように）
    import logging

    logger = logging.getLogger("autoevolve")
    logger.handlers.clear()
    return tmp_path


# --- compute_importance テスト ---


class TestComputeImportanceHighRules:
    """高重要度ルール (0.8-1.0) のテスト。"""

    def test_permission_denied(self):
        score, conf, _fm = compute_importance("error", {"message": "Permission denied"})
        assert score == 0.9
        assert conf == RULE_CONFIDENCE

    def test_eacces(self):
        score, conf, _fm = compute_importance(
            "error", {"message": "EACCES: open failed"}
        )
        assert score == 0.9
        assert conf == RULE_CONFIDENCE

    def test_segfault(self):
        score, conf, _fm = compute_importance("error", {"message": "segfault at 0x0"})
        assert score == 1.0
        assert conf == RULE_CONFIDENCE

    def test_oom(self):
        score, conf, _fm = compute_importance(
            "error", {"message": "OOM killer invoked"}
        )
        assert score == 1.0
        assert conf == RULE_CONFIDENCE

    def test_out_of_memory(self):
        score, conf, _fm = compute_importance("error", {"message": "out of memory"})
        assert score == 1.0
        assert conf == RULE_CONFIDENCE

    def test_golden_principle(self):
        score, conf, _fm = compute_importance("quality", {"rule": "GP-003"})
        assert score == 0.8
        assert conf == RULE_CONFIDENCE

    def test_security(self):
        score, conf, _fm = compute_importance(
            "error", {"message": "SQL injection detected"}
        )
        assert score == 0.9
        assert conf == RULE_CONFIDENCE

    def test_vulnerability(self):
        score, conf, _fm = compute_importance(
            "error", {"message": "vulnerability found"}
        )
        assert score == 0.9
        assert conf == RULE_CONFIDENCE


class TestComputeImportanceMediumRules:
    """中重要度ルール (0.4-0.7) のテスト。"""

    def test_module_not_found(self):
        score, conf, _fm = compute_importance(
            "error", {"message": "ModuleNotFoundError: foo"}
        )
        assert score == 0.5
        assert conf == RULE_CONFIDENCE

    def test_cannot_find_module(self):
        score, conf, _fm = compute_importance(
            "error", {"message": "Cannot find module 'bar'"}
        )
        assert score == 0.5
        assert conf == RULE_CONFIDENCE

    def test_type_error(self):
        score, conf, _fm = compute_importance(
            "error", {"message": "TypeError: x is not a function"}
        )
        assert score == 0.5
        assert conf == RULE_CONFIDENCE

    def test_reference_error(self):
        score, conf, _fm = compute_importance(
            "error", {"message": "ReferenceError: y is not defined"}
        )
        assert score == 0.5
        assert conf == RULE_CONFIDENCE

    def test_timeout(self):
        score, conf, _fm = compute_importance("error", {"message": "ETIMEDOUT"})
        assert score == 0.6
        assert conf == RULE_CONFIDENCE


class TestComputeImportanceLowRules:
    """低重要度ルール (0.0-0.3) のテスト。"""

    def test_warning(self):
        score, conf, _fm = compute_importance(
            "quality", {"message": "warning: unused variable"}
        )
        assert score == 0.2
        assert conf == RULE_CONFIDENCE

    def test_deprecated(self):
        score, conf, _fm = compute_importance(
            "quality", {"message": "this API is deprecated"}
        )
        assert score == 0.3
        assert conf == RULE_CONFIDENCE


class TestComputeImportanceCategoryFallback:
    """ルール未マッチ時のカテゴリベーススコアテスト。"""

    def test_error_category(self):
        score, conf, _fm = compute_importance(
            "error", {"message": "something went wrong"}
        )
        assert score == 0.5
        assert conf == BASE_CONFIDENCE

    def test_quality_category(self):
        score, conf, _fm = compute_importance(
            "quality", {"message": "lint issue found"}
        )
        assert score == 0.6
        assert conf == BASE_CONFIDENCE

    def test_pattern_category(self):
        score, conf, _fm = compute_importance("pattern", {"message": "repeated code"})
        assert score == 0.4
        assert conf == BASE_CONFIDENCE

    def test_correction_category(self):
        score, conf, _fm = compute_importance(
            "correction", {"message": "user corrected"}
        )
        assert score == 0.7
        assert conf == BASE_CONFIDENCE

    def test_unknown_category_defaults_to_05(self):
        score, conf, _fm = compute_importance("unknown", {"message": "something"})
        assert score == 0.5
        assert conf == BASE_CONFIDENCE


# --- emit_event テスト ---


class TestEmitEvent:
    """emit_event がスコアフィールドを含むことを確認。"""

    def test_emit_includes_scoring_fields(self, tmp_path):
        emit_event("error", {"message": "Permission denied on /etc/foo"})
        session_file = tmp_path / "current-session.jsonl"
        assert session_file.exists()

        lines = session_file.read_text().strip().split("\n")
        assert len(lines) == 1

        entry = json.loads(lines[0])
        assert entry["category"] == "error"
        assert entry["message"] == "Permission denied on /etc/foo"
        assert entry["importance"] == 0.9
        assert entry["confidence"] == 0.8
        assert entry["scored_by"] == "rule"
        assert entry["promotion_status"] == "pending"
        assert "timestamp" in entry

    def test_emit_preserves_existing_data(self, tmp_path):
        emit_event(
            "quality",
            {"message": "GP-002 violation", "rule": "GP-002", "file": "main.py"},
        )
        session_file = tmp_path / "current-session.jsonl"
        entry = json.loads(session_file.read_text().strip())

        # 既存データが保持されていること
        assert entry["rule"] == "GP-002"
        assert entry["file"] == "main.py"
        # スコアフィールドも存在
        assert entry["importance"] == 0.8
        assert entry["scored_by"] == "rule"

    def test_emit_multiple_events(self, tmp_path):
        emit_event("error", {"message": "timeout connecting"})
        emit_event("quality", {"message": "deprecated API used"})
        emit_event("pattern", {"message": "normal pattern"})

        session_file = tmp_path / "current-session.jsonl"
        lines = session_file.read_text().strip().split("\n")
        assert len(lines) == 3

        entries = [json.loads(line) for line in lines]
        assert entries[0]["importance"] == 0.6  # timeout
        assert entries[1]["importance"] == 0.3  # deprecated
        assert entries[2]["importance"] == 0.4  # pattern (category fallback)

    def test_emit_then_flush_preserves_scores(self, tmp_path):
        emit_event("error", {"message": "SIGSEGV crash"})
        events = flush_session()

        assert len(events) == 1
        assert events[0]["importance"] == 1.0
        assert events[0]["confidence"] == 0.8
        assert events[0]["scored_by"] == "rule"
        assert events[0]["promotion_status"] == "pending"

        # flush 後はファイルが削除される
        session_file = tmp_path / "current-session.jsonl"
        assert not session_file.exists()


# --- failure_mode / failure_type テスト ---


class TestFailureMode:
    """failure_mode と failure_type の自動付与テスト。"""

    def test_auto_failure_mode_from_rules(self, tmp_path):
        emit_event("error", {"message": "Permission denied"})
        session_file = tmp_path / "current-session.jsonl"
        entry = json.loads(session_file.read_text().strip())
        assert entry["failure_mode"] == "FM-006"
        assert entry["failure_type"] == "generalization"

    def test_auto_failure_mode_gp004(self, tmp_path):
        emit_event("quality", {"rule": "GP-004", "detail": "empty catch"})
        session_file = tmp_path / "current-session.jsonl"
        entry = json.loads(session_file.read_text().strip())
        assert entry["failure_mode"] == "FM-002"

    def test_explicit_failure_mode_overrides_auto(self, tmp_path):
        emit_event("error", {"message": "Permission denied", "failure_mode": "FM-999"})
        session_file = tmp_path / "current-session.jsonl"
        entry = json.loads(session_file.read_text().strip())
        assert entry["failure_mode"] == "FM-999"

    def test_explicit_failure_type(self, tmp_path):
        emit_event("error", {"message": "test", "failure_type": "specification"})
        session_file = tmp_path / "current-session.jsonl"
        entry = json.loads(session_file.read_text().strip())
        assert entry["failure_type"] == "specification"

    def test_no_match_gives_empty_failure_mode(self, tmp_path):
        emit_event("pattern", {"message": "normal pattern"})
        session_file = tmp_path / "current-session.jsonl"
        entry = json.loads(session_file.read_text().strip())
        assert entry["failure_mode"] == ""
        assert entry["failure_type"] == "generalization"

    def test_null_safety_fm001(self):
        _score, _conf, fm = compute_importance(
            "error", {"message": "TypeError: Cannot read properties of undefined"}
        )
        assert fm == "FM-001"

    def test_security_fm010(self):
        _score, _conf, fm = compute_importance(
            "error", {"message": "SQL injection detected"}
        )
        assert fm == "FM-010"


# --- review finding / feedback テスト ---


class TestReviewFinding:
    """レビュー指摘の保存と読み込みテスト。"""

    def test_emit_and_read_finding(self, tmp_path):
        finding = {
            "id": "rf-test-001",
            "reviewer": "code-reviewer",
            "file": "api.go",
            "line": 42,
            "confidence": 85,
            "failure_mode": "FM-002",
            "finding": "エラーが握り潰されている",
            "failure_type": "generalization",
        }
        emit_review_finding(finding)

        pending = read_pending_findings()
        assert len(pending) == 1
        assert pending[0]["id"] == "rf-test-001"
        assert pending[0]["reviewer"] == "code-reviewer"

    def test_feedback_resolves_finding(self, tmp_path):
        emit_review_finding({"id": "rf-test-002", "reviewer": "test", "finding": "x"})
        emit_review_feedback("rf-test-002", "accepted")

        pending = read_pending_findings()
        assert len(pending) == 0

    def test_mixed_pending_and_resolved(self, tmp_path):
        emit_review_finding({"id": "rf-a", "reviewer": "r1", "finding": "x"})
        emit_review_finding({"id": "rf-b", "reviewer": "r2", "finding": "y"})
        emit_review_feedback("rf-a", "ignored")

        pending = read_pending_findings()
        assert len(pending) == 1
        assert pending[0]["id"] == "rf-b"


class TestUpdateFindingOutcome:
    """update_finding_outcome のテスト。"""

    def test_basic_update(self, tmp_path):
        emit_review_finding({"id": "rf-001", "reviewer": "cr", "finding": "bug"})
        result = update_finding_outcome("rf-001", "accept", "explicit")
        assert result is True

        # findings.jsonl に outcome が書き込まれていることを確認
        findings_path = tmp_path / "learnings" / "review-findings.jsonl"
        entry = json.loads(findings_path.read_text().strip())
        assert entry["outcome"] == "accept"
        assert entry["outcome_source"] == "explicit"
        assert "outcome_timestamp" in entry

    def test_explicit_not_overwritten_by_auto_diff(self, tmp_path):
        """R-05: explicit が記録済みなら auto_diff で上書きしない。"""
        emit_review_finding({"id": "rf-002", "reviewer": "cr", "finding": "x"})
        update_finding_outcome("rf-002", "accept", "explicit")

        result = update_finding_outcome("rf-002", "reject", "auto_diff")
        assert result is False

        findings_path = tmp_path / "learnings" / "review-findings.jsonl"
        entry = json.loads(findings_path.read_text().strip())
        assert entry["outcome"] == "accept"
        assert entry["outcome_source"] == "explicit"

    def test_auto_diff_overwritten_by_explicit(self, tmp_path):
        """auto_diff は explicit で上書きできる。"""
        emit_review_finding({"id": "rf-003", "reviewer": "cr", "finding": "x"})
        update_finding_outcome("rf-003", "reject", "auto_diff")
        result = update_finding_outcome("rf-003", "accept", "explicit")
        assert result is True

        findings_path = tmp_path / "learnings" / "review-findings.jsonl"
        entry = json.loads(findings_path.read_text().strip())
        assert entry["outcome"] == "accept"
        assert entry["outcome_source"] == "explicit"

    def test_nonexistent_finding_returns_false(self, tmp_path):
        result = update_finding_outcome("rf-nonexistent", "accept", "explicit")
        assert result is False

    def test_invalid_outcome_returns_false(self, tmp_path):
        emit_review_finding({"id": "rf-004", "reviewer": "cr", "finding": "x"})
        result = update_finding_outcome("rf-004", "invalid_value", "explicit")
        assert result is False

    def test_outcome_resolves_pending(self, tmp_path):
        """outcome が設定された finding は pending から消える。"""
        emit_review_finding({"id": "rf-005", "reviewer": "cr", "finding": "x"})
        emit_review_finding({"id": "rf-006", "reviewer": "cr", "finding": "y"})
        update_finding_outcome("rf-005", "accept", "explicit")

        pending = read_pending_findings()
        assert len(pending) == 1
        assert pending[0]["id"] == "rf-006"


# --- skill tracking テスト ---


class TestEmitSkillEvent:
    """スキル実行イベントの記録テスト。"""

    def test_emit_skill_invocation(self, tmp_path):
        emit_skill_event(
            "invocation",
            {
                "skill_name": "review",
                "session_id": "test-session-001",
            },
        )
        session_file = tmp_path / "current-session.jsonl"
        assert session_file.exists()

        entry = json.loads(session_file.read_text().strip())
        assert entry["category"] == "skill"
        assert entry["type"] == "invocation"
        assert entry["skill_name"] == "review"

    def test_emit_skill_event_requires_skill_name(self, tmp_path):
        with pytest.raises(ValueError, match="skill_name"):
            emit_skill_event("invocation", {"session_id": "abc"})

    def test_emit_skill_outcome(self, tmp_path):
        emit_skill_event(
            "outcome",
            {
                "skill_name": "search-first",
                "score": 0.35,
                "error_count": 2,
                "gp_violations": 1,
                "review_criticals": 0,
                "test_passed": False,
            },
        )
        session_file = tmp_path / "current-session.jsonl"
        entry = json.loads(session_file.read_text().strip())
        assert entry["category"] == "skill"
        assert entry["type"] == "outcome"
        assert entry["score"] == 0.35


class TestComputeSkillScore:
    """スキルの複合スコア計算テスト (1-10 スケール)。"""

    def test_perfect_session(self):
        events = [
            {"category": "skill", "type": "invocation", "skill_name": "review"},
        ]
        score = compute_skill_score(events, "review")
        # 5.0 + 1.5(no err) + 1.0(test ok) + 0.5(no GP) + 0.5(no rev) = 8.5
        assert score == pytest.approx(8.5)

    def test_session_with_errors(self):
        events = [
            {"category": "skill", "type": "invocation", "skill_name": "review"},
            {"category": "error", "message": "TypeError"},
            {"category": "error", "message": "ReferenceError"},
        ]
        score = compute_skill_score(events, "review")
        # 5.0 - 3.0(2err) + 1.0(test ok) + 0.5(no GP) + 0.5(no rev) = 4.0
        assert score == pytest.approx(4.0)

    def test_session_with_test_failure(self):
        events = [
            {"category": "skill", "type": "invocation", "skill_name": "review"},
            {"category": "pattern", "message": "test_failed", "test_passed": False},
        ]
        score = compute_skill_score(events, "review")
        # 5.0 + 1.5(no err) - 2.5(test fail) + 0.5(no GP) + 0.5(no rev) = 5.0
        assert score == pytest.approx(5.0)

    def test_session_with_gp_violations(self):
        events = [
            {"category": "skill", "type": "invocation", "skill_name": "review"},
            {"category": "quality", "rule": "GP-001"},
            {"category": "quality", "rule": "GP-003"},
            {"category": "quality", "rule": "GP-004"},
        ]
        score = compute_skill_score(events, "review")
        # 5.0 + 1.5(no err) + 1.0(test ok) - 1.5(3GP) + 0.5(no rev) = 6.5
        assert score == pytest.approx(6.5)

    def test_score_clamps_to_minimum(self):
        events = [
            {"category": "skill", "type": "invocation", "skill_name": "bad-skill"},
            {"category": "error", "message": "err1"},
            {"category": "error", "message": "err2"},
            {"category": "error", "message": "err3"},
            {"category": "pattern", "message": "test_failed", "test_passed": False},
        ]
        score = compute_skill_score(events, "bad-skill")
        # 5.0 - 4.5(3err) - 2.5(test) + 0.5(no GP) + 0.5(no rev) = -1.0 → 1.0
        assert score == 1.0

    def test_review_criticals_penalty(self):
        events = [
            {"category": "skill", "type": "invocation", "skill_name": "rpi"},
            {"category": "quality", "review_severity": "critical"},
            {"category": "quality", "review_severity": "important"},
        ]
        score = compute_skill_score(events, "rpi")
        # 5.0 + 1.5(no err) + 1.0(test ok) + 0.5(no GP) - 2.0(2rev) = 6.0
        assert score == pytest.approx(6.0)

    def test_rust_nested_events_are_normalized(self):
        """CRIT-001: Rust hook の data ラップ形式でもスコアが正しく計算される。"""
        events = [
            {"category": "skill", "type": "invocation", "skill_name": "review"},
            {
                "category": "error",
                "data": {"message": "TypeError", "command": "npm test"},
            },
            {
                "category": "quality",
                "data": {"rule": "GP-004", "file": "test.py"},
            },
        ]
        score = compute_skill_score(events, "review")
        # 5.0 - 1.5(1err) + 1.0(test ok) - 0.5(1GP) + 0.5(no rev) = 4.5
        assert score == pytest.approx(4.5)

    def test_mixed_rust_and_python_events(self):
        """CRIT-001: Rust/Python 混在イベントでもスコアが正しく計算される。"""
        events = [
            {"category": "error", "message": "err1"},
            {"category": "error", "data": {"message": "err2", "command": "cargo"}},
        ]
        score = compute_skill_score(events, "test-skill")
        # 5.0 - 3.0(2err) + 1.0(test ok) + 0.5(no GP) + 0.5(no rev) = 4.0
        assert score == pytest.approx(4.0)

    def test_per_skill_attribution(self):
        """Per-skill attribution: 他スキルのイベントがスコアに影響しない。"""
        events = [
            {"category": "skill", "type": "invocation", "skill_name": "review"},
            {"category": "skill", "type": "invocation", "skill_name": "commit"},
            # review に帰属されるエラー
            {"category": "error", "message": "err1", "skill_name": "review"},
            # commit に帰属されるエラー（review のスコアに影響しない）
            {"category": "error", "message": "err2", "skill_name": "commit"},
            {"category": "error", "message": "err3", "skill_name": "commit"},
        ]
        review_score = compute_skill_score(events, "review")
        commit_score = compute_skill_score(events, "commit")
        # review: 1 error → 5.0 - 1.5 + 1.0 + 0.5 + 0.5 = 5.5
        assert review_score == pytest.approx(5.5)
        # commit: 2 errors → 5.0 - 3.0 + 1.0 + 0.5 + 0.5 = 4.0
        assert commit_score == pytest.approx(4.0)
        assert review_score > commit_score


class TestNormalizeEvent:
    """_normalize_event の単体テスト。"""

    def test_flat_event_unchanged(self):
        event = {"category": "error", "message": "TypeError"}
        assert _normalize_event(event) == event

    def test_nested_data_flattened(self):
        event = {
            "category": "error",
            "importance": 0.5,
            "data": {"message": "TypeError", "command": "npm test"},
        }
        result = _normalize_event(event)
        assert result["category"] == "error"
        assert result["message"] == "TypeError"
        assert result["command"] == "npm test"
        assert result["importance"] == 0.5
        assert "data" not in result

    def test_non_dict_data_unchanged(self):
        event = {"category": "quality", "data": "string-value"}
        assert _normalize_event(event) == event

    def test_top_level_keys_not_overwritten_by_data(self):
        """I-2: data 内のキーがトップレベルキーを上書きしないことを検証。"""
        event = {
            "category": "error",
            "importance": 0.8,
            "data": {"category": "pattern", "importance": 0.1, "message": "test"},
        }
        result = _normalize_event(event)
        # Top-level keys must be preserved
        assert result["category"] == "error"
        assert result["importance"] == 0.8
        # data-only keys are merged
        assert result["message"] == "test"


class TestEmitSkillStep:
    """スキルステップの成否記録テスト。"""

    def test_emit_step_success(self, tmp_path):
        emit_skill_step("review", step=1, outcome="success")
        session_file = tmp_path / "current-session.jsonl"
        entry = json.loads(session_file.read_text().strip())
        assert entry["category"] == "skill"
        assert entry["type"] == "step_outcome"
        assert entry["skill_name"] == "review"
        assert entry["step"] == 1
        assert entry["outcome"] == "success"

    def test_emit_step_failed_with_error_ref(self, tmp_path):
        emit_skill_step(
            "react-expert",
            step=3,
            outcome="failed",
            data={"error_ref": "2026-03-14T10:23:45Z", "tool_name": "WebFetch"},
        )
        session_file = tmp_path / "current-session.jsonl"
        entry = json.loads(session_file.read_text().strip())
        assert entry["outcome"] == "failed"
        assert entry["step"] == 3
        assert entry["error_ref"] == "2026-03-14T10:23:45Z"
        assert entry["tool_name"] == "WebFetch"

    def test_emit_step_skipped(self, tmp_path):
        emit_skill_step("spike", step=2, outcome="skipped")
        session_file = tmp_path / "current-session.jsonl"
        entry = json.loads(session_file.read_text().strip())
        assert entry["outcome"] == "skipped"


# --- AgentRx-inspired FM-011~015 テスト ---


class TestAgentBehaviorFailureModes:
    """FM-011~015: エージェント行動の失敗分類テスト。"""

    def test_fm011_plan_adherence(self):
        _score, _conf, fm = compute_importance(
            "error", {"message": "incomplete plan: step 3 not executed"}
        )
        assert fm == "FM-011"

    def test_fm012_information_invention_enoent(self):
        _score, _conf, fm = compute_importance(
            "error",
            {"message": "ENOENT: no such file or directory, open '/src/foo.ts'"},
        )
        assert fm == "FM-012"

    def test_fm012_information_invention_no_such_file(self):
        _score, _conf, fm = compute_importance(
            "error", {"message": "No such file or directory"}
        )
        assert fm == "FM-012"

    def test_fm012_information_invention_404(self):
        _score, _conf, fm = compute_importance("error", {"message": "404 Not Found"})
        assert fm == "FM-012"

    def test_fm012_does_not_exist(self):
        _score, _conf, fm = compute_importance(
            "error", {"message": "path /foo/bar does not exist"}
        )
        assert fm == "FM-012"

    def test_fm014_intent_misalignment_ja(self):
        _score, _conf, fm = compute_importance(
            "correction", {"message": "違う、そうじゃなくて別のファイル"}
        )
        assert fm == "FM-014"

    def test_fm014_intent_misalignment_en(self):
        _score, _conf, fm = compute_importance(
            "correction", {"message": "not what I asked for"}
        )
        assert fm == "FM-014"

    def test_fm015_premature_action(self):
        _score, _conf, fm = compute_importance(
            "error", {"message": "premature action: git push without confirm"}
        )
        assert fm == "FM-015"
