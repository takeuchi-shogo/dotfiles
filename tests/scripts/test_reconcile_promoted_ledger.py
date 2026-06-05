import importlib.util
import json
from pathlib import Path

import pytest

_SPEC = importlib.util.spec_from_file_location(
    "rpl",
    Path(__file__).resolve().parents[2]
    / ".config/claude/scripts/learner/reconcile-promoted-ledger.py",
)
rpl = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(rpl)

# 有効な冪等キーは 40 桁 hex (SHA1)。テスト用に決め打ちの hex を使う。
KEY_A = "a" * 40
KEY_B = "b" * 40


def _write_manifest(path, promotions):
    path.write_text(
        json.dumps({"promotions": promotions}, ensure_ascii=False),
        encoding="utf-8",
    )


def _ledger_keys(ledger):
    return rpl.load_ledger_keys(ledger)


def test_appends_adopted_and_rejected(tmp_path):
    mdir = tmp_path / "manifests"
    mdir.mkdir()
    _write_manifest(
        mdir / "20260606.json",
        [
            {"key": KEY_A, "decision": "adopted", "target_artifact": "x.md"},
            {"key": KEY_B, "decision": "rejected", "scope": "cc"},
        ],
    )
    ledger = tmp_path / "promoted-ledger.jsonl"
    result = rpl.reconcile(mdir, ledger, dry_run=False)
    assert result["appended"] == 2
    assert _ledger_keys(ledger) == {KEY_A, KEY_B}


def test_skips_unknown_decision_and_missing_key(tmp_path):
    mdir = tmp_path / "manifests"
    mdir.mkdir()
    _write_manifest(
        mdir / "m.json",
        [
            {"key": KEY_A, "decision": "adopted"},
            {"key": KEY_B, "decision": "deferred"},  # 未知 decision → 入れない
            {"decision": "adopted"},  # key 欠落 → 入れない
        ],
    )
    ledger = tmp_path / "promoted-ledger.jsonl"
    result = rpl.reconcile(mdir, ledger, dry_run=False)
    assert result["appended"] == 1
    assert _ledger_keys(ledger) == {KEY_A}


def test_skips_invalid_key_format(tmp_path):
    mdir = tmp_path / "manifests"
    mdir.mkdir()
    _write_manifest(
        mdir / "m.json",
        [
            {"key": "not-a-sha1", "decision": "adopted"},  # 40-hex でない → skip
            {
                "key": KEY_A.upper(),
                "decision": "adopted",
            },  # 大文字 hex → skip (小文字のみ)
            {"key": KEY_B, "decision": "adopted"},  # 有効
        ],
    )
    ledger = tmp_path / "promoted-ledger.jsonl"
    result = rpl.reconcile(mdir, ledger, dry_run=False)
    assert result["appended"] == 1
    assert _ledger_keys(ledger) == {KEY_B}


def test_dedup_within_single_manifest(tmp_path):
    mdir = tmp_path / "manifests"
    mdir.mkdir()
    _write_manifest(
        mdir / "m.json",
        [
            {"key": KEY_A, "decision": "adopted"},
            {"key": KEY_A, "decision": "rejected"},  # 同一 manifest 内重複 → 1 件のみ
        ],
    )
    ledger = tmp_path / "promoted-ledger.jsonl"
    result = rpl.reconcile(mdir, ledger, dry_run=False)
    assert result["appended"] == 1
    assert _ledger_keys(ledger) == {KEY_A}


def test_idempotent_against_existing_ledger(tmp_path):
    mdir = tmp_path / "manifests"
    mdir.mkdir()
    _write_manifest(
        mdir / "m.json",
        [{"key": KEY_A, "decision": "adopted"}, {"key": KEY_B, "decision": "adopted"}],
    )
    ledger = tmp_path / "promoted-ledger.jsonl"
    ledger.write_text(
        json.dumps({"key": KEY_A, "decision": "adopted"}) + "\n", encoding="utf-8"
    )
    result = rpl.reconcile(mdir, ledger, dry_run=False)
    assert result["appended"] == 1  # KEY_A は既存なので KEY_B のみ
    assert result["skipped"] == 1
    assert _ledger_keys(ledger) == {KEY_A, KEY_B}


def test_appends_without_trailing_newline(tmp_path):
    mdir = tmp_path / "manifests"
    mdir.mkdir()
    _write_manifest(mdir / "m.json", [{"key": KEY_B, "decision": "adopted"}])
    ledger = tmp_path / "promoted-ledger.jsonl"
    # 末尾改行なしの既存 ledger (結合バグの回帰テスト)
    ledger.write_text(
        json.dumps({"key": KEY_A, "decision": "adopted"}), encoding="utf-8"
    )
    rpl.reconcile(mdir, ledger, dry_run=False)
    lines = [ln for ln in ledger.read_text().splitlines() if ln.strip()]
    assert len(lines) == 2  # 2 行に分離されている
    assert _ledger_keys(ledger) == {KEY_A, KEY_B}


def test_dedup_same_key_across_manifests(tmp_path):
    mdir = tmp_path / "manifests"
    mdir.mkdir()
    _write_manifest(mdir / "1.json", [{"key": KEY_A, "decision": "adopted"}])
    _write_manifest(mdir / "2.json", [{"key": KEY_A, "decision": "rejected"}])
    ledger = tmp_path / "promoted-ledger.jsonl"
    result = rpl.reconcile(mdir, ledger, dry_run=False)
    assert result["appended"] == 1  # 同一 key は 1 度だけ
    assert _ledger_keys(ledger) == {KEY_A}


def test_dry_run_no_write(tmp_path):
    mdir = tmp_path / "manifests"
    mdir.mkdir()
    _write_manifest(mdir / "m.json", [{"key": KEY_A, "decision": "adopted"}])
    ledger = tmp_path / "promoted-ledger.jsonl"
    result = rpl.reconcile(mdir, ledger, dry_run=True)
    assert result["appended"] == 1
    assert result["dry_run"] is True
    assert not ledger.exists()  # 副作用なし


def test_empty_manifest_dir(tmp_path):
    mdir = tmp_path / "manifests"
    mdir.mkdir()
    ledger = tmp_path / "promoted-ledger.jsonl"
    result = rpl.reconcile(mdir, ledger, dry_run=False)
    assert result["appended"] == 0
    assert not ledger.exists()


def test_tolerant_to_broken_manifest(tmp_path):
    mdir = tmp_path / "manifests"
    mdir.mkdir()
    (mdir / "broken.json").write_text("{not json", encoding="utf-8")
    _write_manifest(mdir / "ok.json", [{"key": KEY_A, "decision": "adopted"}])
    ledger = tmp_path / "promoted-ledger.jsonl"
    result = rpl.reconcile(mdir, ledger, dry_run=False)
    assert result["appended"] == 1  # 壊れた manifest は skip、健全な方は処理
    assert _ledger_keys(ledger) == {KEY_A}


def test_strict_ledger_raises_on_corrupt_line(tmp_path):
    mdir = tmp_path / "manifests"
    mdir.mkdir()
    _write_manifest(mdir / "m.json", [{"key": KEY_A, "decision": "adopted"}])
    ledger = tmp_path / "promoted-ledger.jsonl"
    # ledger は正本: 壊れた行は無言 skip せず例外で surface する
    ledger.write_text("{corrupt ledger line\n", encoding="utf-8")
    with pytest.raises(ValueError):
        rpl.reconcile(mdir, ledger, dry_run=False)
