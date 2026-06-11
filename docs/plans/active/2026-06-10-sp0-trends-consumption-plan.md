---
status: active
---

# SP0: Trends 消費層 (②) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** adoption-ledger.jsonl の採用記事を clickable に surface する消費層（`task trends` + その日初回シェルの digest）を作り、tech-researcher の下流断線を解消する。

**Architecture:** 単一ソース = `~/.cache/tech-researcher/adoption-ledger.jsonl`。共通コア `trends_select.py`（純ロジック、aggregate.py と同パターン）を pull（Taskfile）と push（zsh first-open digest）が共有。新 DB・常駐プロセスなし（設計制約 C4: 浅い consumer）。

**Tech Stack:** Python 3 (argparse, stdlib のみ) / pytest (`uv run pytest`) / Taskfile / zsh snippet (`.config/zsh/functions/` 自動 source)。

**Spec:** `docs/superpowers/specs/2026-06-10-knowledge-intake-pipeline-design.md`（§6 SP0。**Phase 1 のみ**実装。Phase 2 = 朝 Discord push + 朝 wake は §9 撤退条件「Phase 1 稼働2週間の使用実績」と §6.4 pmset sudo 検証を通過後に別プランで扱う）

---

## Prerequisites / 執行コンテキスト

- **Worktree**: `.claude/worktrees/knowledge-intake-design`（branch `docs/knowledge-intake-pipeline`、base = origin/master bb1d9fd）。この worktree でそのまま実装し、design doc + plan + 実装を**1 PR** にまとめる（① PR #71 と同様の単位）。
- **Pre-commit 注意**: `build-claude-check` hook は symlink 経由でメインリポジトリ checkout の CLAUDE.md drift を検査する。別セッションのブランチに drift があると**この worktree のコミットもブロックされる**。その場合は drift 解消（別セッション側 `task build-claude`）を待つ。**`git commit --no-verify` は禁止（settings.json deny）**。
- **Taskfile への追記はコメント行を入れない**（comment-guard hook が既存ファイルへの新規 `#` コメント追加をブロックする。`desc:` で意図を表現する）。
- テスト実行: `uv run pytest`（既存 test_aggregate.py の docstring 準拠）。uv が無い環境では `python3 -m pytest` に読み替え。

---

### Task 1: trends_select.py — 選別ロジック `select()` (TDD)

**Files:**
- Create: `scripts/runtime/tech-researcher/trends_select.py`
- Create: `scripts/runtime/tech-researcher/tests/test_trends_select.py`

- [ ] **Step 1: Write the failing test**

`scripts/runtime/tech-researcher/tests/test_trends_select.py` を以下の内容で作成:

```python
"""trends_select.py の純ロジック検証。

実行: uv run pytest scripts/runtime/tech-researcher/tests/test_trends_select.py
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import trends_select  # noqa: E402

ASOF = date(2026, 6, 10)


def _line(
    d: str,
    url: str,
    adopted: bool = True,
    novelty: int | None = 3,
    reliability: int | None = 3,
    concreteness: int | None = 3,
    title: str = "t",
    domain: str = "example.com",
) -> str:
    scores = None
    if novelty is not None:
        scores = {
            "novelty": novelty,
            "reliability": reliability,
            "concreteness": concreteness,
        }
    return json.dumps(
        {
            "ts": f"{d}T00:00:00+09:00",
            "date": d,
            "domain": domain,
            "url": url,
            "title": title,
            "adopted": adopted,
            "source_id": "https://feed.example/rss",
            "scores": scores,
        },
        ensure_ascii=False,
    )


def test_adopted_false_excluded():
    lines = [
        _line("2026-06-09", "https://a/1"),
        _line("2026-06-09", "https://a/2", adopted=False),
    ]
    items = trends_select.select(lines, asof=ASOF, days=3)
    assert [r["url"] for r in items] == ["https://a/1"]


def test_window_cutoff_excludes_old():
    lines = [
        _line("2026-06-09", "https://a/new"),
        _line("2026-06-01", "https://a/old"),
    ]
    items = trends_select.select(lines, asof=ASOF, days=3)
    assert [r["url"] for r in items] == ["https://a/new"]


def test_url_dedup_keeps_latest_date():
    lines = [
        _line("2026-06-08", "https://a/1", novelty=1, reliability=1, concreteness=1),
        _line("2026-06-09", "https://a/1", novelty=5, reliability=5, concreteness=5),
    ]
    items = trends_select.select(lines, asof=ASOF, days=7)
    assert len(items) == 1
    assert items[0]["date"] == "2026-06-09"


def test_sort_score_desc_then_reliability_then_date():
    lines = [
        _line("2026-06-09", "https://low", novelty=2, concreteness=2, reliability=5),
        _line("2026-06-09", "https://high", novelty=5, concreteness=4, reliability=1),
        _line("2026-06-09", "https://tie-rel5", novelty=4, concreteness=4, reliability=5),
        _line("2026-06-09", "https://tie-rel2", novelty=4, concreteness=4, reliability=2),
        _line("2026-06-09", "https://tie-new", novelty=3, concreteness=3, reliability=3),
        _line("2026-06-08", "https://tie-old", novelty=3, concreteness=3, reliability=3),
    ]
    items = trends_select.select(lines, asof=ASOF, days=7)
    urls = [r["url"] for r in items]
    assert urls == [
        "https://high",      # novelty+concreteness=9
        "https://tie-rel5",  # 8, reliability=5
        "https://tie-rel2",  # 8, reliability=2
        "https://tie-new",   # 6, 同点 → date 降順
        "https://tie-old",   # 6
        "https://low",       # 4
    ]


def test_scores_null_ranks_last():
    lines = [
        _line("2026-06-09", "https://scored", novelty=1, concreteness=1, reliability=1),
        _line("2026-06-09", "https://null", novelty=None),
    ]
    items = trends_select.select(lines, asof=ASOF, days=3)
    assert [r["url"] for r in items] == ["https://scored", "https://null"]


def test_top_limit():
    lines = [_line("2026-06-09", f"https://a/{i}") for i in range(10)]
    items = trends_select.select(lines, asof=ASOF, days=3, top=4)
    assert len(items) == 4


def test_malformed_and_blank_lines_skipped():
    lines = ["not json", "", _line("2026-06-09", "https://a/1")]
    items = trends_select.select(lines, asof=ASOF, days=3)
    assert len(items) == 1


def test_missing_url_skipped():
    rec = json.loads(_line("2026-06-09", "https://a/1"))
    del rec["url"]
    items = trends_select.select([json.dumps(rec)], asof=ASOF, days=3)
    assert items == []
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd .claude/worktrees/knowledge-intake-design && uv run pytest scripts/runtime/tech-researcher/tests/test_trends_select.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'trends_select'`

- [ ] **Step 3: Write minimal implementation**

`scripts/runtime/tech-researcher/trends_select.py` を以下の内容で作成:

```python
#!/usr/bin/env python3
"""trends_select.py — adoption-ledger から adopted 記事をランク付けして出力する (read-only)。

(2) 消費層 (SP0) の共通コア。pull (task trends) / push (zsh first-open digest、将来の
朝 Discord push) が本モジュールを共有し、ランキング・描画ロジックの重複を防ぐ。

ランク: novelty+concreteness 降順 → reliability 降順 → date 降順。
scores 不在 (旧形式レコードは null) は 0 扱いで末尾に落ちる。

Usage:
    trends_select.py <ledger.jsonl> [--days N] [--top K] [--asof YYYY-MM-DD] [--format term|json]

設計: docs/superpowers/specs/2026-06-10-knowledge-intake-pipeline-design.md §6.1
純ロジック: 引数の ledger path とオプションのみに依存し副作用を持たない。
"""

from __future__ import annotations

import json
from datetime import date, timedelta


def select(lines, asof: date, days: int, top: int | None = None) -> list[dict]:
    """ledger 行から adopted=true を日付窓内で抽出し、url dedup + score ソート済みで返す。"""
    cutoff = (asof - timedelta(days=days)).isoformat()
    asof_s = asof.isoformat()
    seen: dict[str, dict] = {}
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue  # ledger は append-only。他 writer 由来の不正行で全体を落とさない
        if not isinstance(rec, dict) or not rec.get("adopted"):
            continue
        d = rec.get("date") or ""
        if not (cutoff <= d <= asof_s):
            continue
        url = rec.get("url")
        if not url:
            continue
        prev = seen.get(url)
        if prev is None or d > (prev.get("date") or ""):
            seen[url] = rec

    # 安定ソート 2 段: date 降順で並べてから score key で再ソート → 同点は新しい日付が先に残る
    items = sorted(seen.values(), key=lambda r: r.get("date") or "", reverse=True)

    def score_key(rec: dict):
        s = rec.get("scores") or {}
        nov = s.get("novelty") or 0
        con = s.get("concreteness") or 0
        rel = s.get("reliability") or 0
        return (-(nov + con), -rel)

    items.sort(key=score_key)
    return items[:top] if top else items
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest scripts/runtime/tech-researcher/tests/test_trends_select.py -v`
Expected: PASS (8 passed)

- [ ] **Step 5: Commit**

```bash
git add scripts/runtime/tech-researcher/trends_select.py scripts/runtime/tech-researcher/tests/test_trends_select.py
git commit -m "✨ feat(trends): trends_select.py 選別コア — adoption-ledger の下流 consumer 第1号

intent(trends): tech-researcher 下流断線の解消 (SP0)。ledger を単一ソースに消費層を作る
decision(ranking): novelty+concreteness 降順 → reliability → date 降順。scores null は 0 扱いで末尾"
```

---

### Task 2: trends_select.py — 描画 + CLI (TDD)

**Files:**
- Modify: `scripts/runtime/tech-researcher/trends_select.py`（Task 1 で作成済み、末尾に追記）
- Modify: `scripts/runtime/tech-researcher/tests/test_trends_select.py`（末尾に追記）

- [ ] **Step 1: Write the failing tests**

`tests/test_trends_select.py` の末尾に追記:

```python
def test_render_term_contains_urls_in_rank_order():
    lines = [
        _line("2026-06-09", "https://high", novelty=5, concreteness=5, title="High"),
        _line("2026-06-09", "https://low", novelty=1, concreteness=1, title="Low"),
    ]
    items = trends_select.select(lines, asof=ASOF, days=3)
    out = trends_select.render_term(items, days=3)
    assert "https://high" in out and "https://low" in out
    assert out.index("https://high") < out.index("https://low")
    assert "High" in out and "example.com" in out


def test_render_term_empty():
    out = trends_select.render_term([], days=3)
    assert "採用記事なし" in out


def test_render_json_roundtrip():
    lines = [_line("2026-06-09", "https://a/1")]
    items = trends_select.select(lines, asof=ASOF, days=3)
    parsed = json.loads(trends_select.render_json(items))
    assert parsed[0]["url"] == "https://a/1"


def test_main_missing_ledger_exits_zero(tmp_path, capsys):
    rc = trends_select.main([str(tmp_path / "none.jsonl"), "--asof", "2026-06-10"])
    assert rc == 0
    assert "採用記事なし" in capsys.readouterr().out


def test_main_invalid_asof_exits_two(tmp_path, capsys):
    rc = trends_select.main([str(tmp_path / "none.jsonl"), "--asof", "junk"])
    assert rc == 2


def test_main_renders_real_file(tmp_path, capsys):
    ledger = tmp_path / "ledger.jsonl"
    ledger.write_text(_line("2026-06-09", "https://a/1", title="Article") + "\n")
    rc = trends_select.main([str(ledger), "--asof", "2026-06-10", "--days", "3"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "https://a/1" in out and "Article" in out
```

- [ ] **Step 2: Run tests to verify the new ones fail**

Run: `uv run pytest scripts/runtime/tech-researcher/tests/test_trends_select.py -v`
Expected: 8 passed (Task 1), 6 FAILED — `AttributeError: module 'trends_select' has no attribute 'render_term'`

- [ ] **Step 3: Implement render + CLI**

`trends_select.py` の import 部を以下に差し替え:

```python
from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime, timedelta
```

ファイル末尾に追記:

```python
def render_term(items: list[dict], days: int) -> str:
    """ターミナル向け表示。URL は素のまま出力 (Ghostty 等が自動でリンク化する)。"""
    out = [f"📡 AI Tech Trends — 直近{days}日 (adoption-ledger)"]
    if not items:
        out.append(f"  (直近{days}日の採用記事なし)")
        return "\n".join(out) + "\n"
    for i, rec in enumerate(items, 1):
        s = rec.get("scores") or {}
        badge = (
            f"n{s.get('novelty') or '-'}"
            f" c{s.get('concreteness') or '-'}"
            f" r{s.get('reliability') or '-'}"
        )
        title = (rec.get("title") or "(no title)")[:72]
        day = (rec.get("date") or "")[5:]
        out.append(f" {i:>2}. [{badge}] {title}  ({rec.get('domain', '?')}, {day})")
        out.append(f"     {rec['url']}")
    return "\n".join(out) + "\n"


def render_json(items: list[dict]) -> str:
    return json.dumps(items, ensure_ascii=False)


def _parse_date(s: str) -> date | None:
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError:
        return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ledger", help="adoption-ledger.jsonl path")
    parser.add_argument("--days", type=int, default=3)
    parser.add_argument("--top", type=int, default=5)
    parser.add_argument("--asof", default=None, help="基準日 YYYY-MM-DD (既定: 今日)")
    parser.add_argument("--format", choices=("term", "json"), default="term")
    args = parser.parse_args(argv)

    asof = _parse_date(args.asof) if args.asof else date.today()
    if asof is None:
        print(f"ERROR: invalid --asof: {args.asof}", file=sys.stderr)
        return 2
    if args.days < 1 or args.top < 1:
        print("ERROR: --days and --top must be >= 1", file=sys.stderr)
        return 2

    try:
        with open(args.ledger, encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        lines = []  # ledger 未生成 = 空表示。zsh hook から安全に呼べるようエラーにしない

    items = select(lines, asof=asof, days=args.days, top=args.top)
    if args.format == "json":
        sys.stdout.write(render_json(items) + "\n")
    else:
        sys.stdout.write(render_term(items, days=args.days))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run tests to verify all pass**

Run: `uv run pytest scripts/runtime/tech-researcher/tests/test_trends_select.py -v`
Expected: PASS (14 passed)

- [ ] **Step 5: 実 ledger でスモーク確認 (read-only)**

Run: `python3 scripts/runtime/tech-researcher/trends_select.py "$HOME/.cache/tech-researcher/adoption-ledger.jsonl" --days 7 --top 5`
Expected: 実在の採用記事が score badge + URL 付きで最大5件表示される（ledger には 2026-06-06〜09 の adopted 約29件が存在）

- [ ] **Step 6: Commit**

```bash
git add scripts/runtime/tech-researcher/trends_select.py scripts/runtime/tech-researcher/tests/test_trends_select.py
git commit -m "✨ feat(trends): render_term/render_json + CLI — aggregate.py と同 main(argv) パターン"
```

---

### Task 3: Taskfile `trends` target（pull 導線 + 使用ログ）

**Files:**
- Modify: `Taskfile.yml`（末尾の `nightly:wake:status:` ターゲットの後に追記）

- [ ] **Step 1: Add target**

`Taskfile.yml` 末尾（`nightly:wake:status:` ブロックの後）に追記。**コメント行は入れない**（comment-guard）:

```yaml
  trends:
    desc: 'Show top adopted AI tech trends from adoption-ledger (clickable URLs; DAYS/TOP override 可, 使用は trends-usage.log に記録 — design §9 撤退条件の評価データ)'
    vars:
      DAYS: '{{.DAYS | default "3"}}'
      TOP: '{{.TOP | default "5"}}'
    cmds:
      - mkdir -p $HOME/.cache/tech-researcher
      - date -Iseconds >> $HOME/.cache/tech-researcher/trends-usage.log
      - python3 {{.TASKFILE_DIR}}/scripts/runtime/tech-researcher/trends_select.py $HOME/.cache/tech-researcher/adoption-ledger.jsonl --days {{.DAYS}} --top {{.TOP}}
```

- [ ] **Step 2: Verify**

Run: `task trends`
Expected: 直近3日の top5 が表示される。

Run: `task trends DAYS=7 TOP=10`
Expected: 窓と件数が変わる。

Run: `tail -2 ~/.cache/tech-researcher/trends-usage.log`
Expected: ISO timestamp が 2 行（上の2回分）追記されている。

- [ ] **Step 3: Commit**

```bash
git add Taskfile.yml
git commit -m "✨ feat(trends): task trends — pull 導線 + 使用ログ

intent(trends): 撤退条件 (design §9: 2週間未使用なら縮退) を評価可能にするため使用を記録
decision(usage-log): Taskfile cmd 1行で date -Iseconds 追記。新しい計測機構は作らない (KISS)"
```

---

### Task 4: zsh first-open digest（push① 導線）

**Files:**
- Create: `.config/zsh/functions/trends-digest.zsh`（`.config/zsh/.zshrc` の for ループが `functions/*.zsh` を自動 source するため、ファイルを置くだけで配線完了。zshrc の編集不要）

- [ ] **Step 1: Create snippet**

`.config/zsh/functions/trends-digest.zsh` を以下の内容で作成:

```zsh
# trends-digest.zsh — その日最初の interactive shell で AI トレンド digest を表示する。
# 1日1回ガード: ~/.cache/tech-researcher/digest-shown-YYYY-MM-DD (空 stamp)。
# stamp ヒット時は即 return し起動オーバーヘッドを ~1ms に抑える。ledger 不在なら何もしない。
# python 失敗時も stamp は書く (シェル起動ごとの再試行 nag を防ぐ)。ただし WARN は 1 回見せる。
# 設計: docs/superpowers/specs/2026-06-10-knowledge-intake-pipeline-design.md §6.2
_trends_digest_on_first_open() {
  [[ -o interactive ]] || return 0
  local cache_dir="$HOME/.cache/tech-researcher"
  local today stamp ledger
  today="$(date +%Y-%m-%d)"
  stamp="$cache_dir/digest-shown-$today"
  [[ -f "$stamp" ]] && return 0
  ledger="$cache_dir/adoption-ledger.jsonl"
  [[ -f "$ledger" ]] || return 0
  mkdir -p "$cache_dir"
  if ! python3 "$HOME/dotfiles/scripts/runtime/tech-researcher/trends_select.py" \
      "$ledger" --days 3 --top 5; then
    print -u2 "[trends-digest] WARN: trends_select.py failed (今日は再表示しません)"
  fi
  rm -f "$cache_dir"/digest-shown-* 2>/dev/null
  : > "$stamp"
}
_trends_digest_on_first_open
```

- [ ] **Step 2: Verify first-open behavior**

Run: `rm -f ~/.cache/tech-researcher/digest-shown-*; zsh -ic 'true' 2>&1 | head -15`
Expected: digest（📡 AI Tech Trends ... + URL）が表示される

Run: `zsh -ic 'true' 2>&1 | head -3`
Expected: 何も表示されない（stamp ヒット）

Run: `ls ~/.cache/tech-researcher/digest-shown-*`
Expected: 今日の日付の stamp が 1 個だけ存在する

- [ ] **Step 3: Verify startup overhead (stamp hit path)**

Run: `time zsh -ic 'true'`
Expected: stamp ありの状態で、このスニペット起因の体感遅延がない（全体が従来同等。digest 表示パスは1日1回のみ python を起動する）

- [ ] **Step 4: Commit**

```bash
git add .config/zsh/functions/trends-digest.zsh
git commit -m "✨ feat(trends): zsh first-open digest — その日初回シェルに当日トレンドを表示

intent(trends): 『そもそも見てない』対策。実際に使う面 (ターミナル) に朝トリガーを置く
decision(stamp): 日付付き空 stamp で1日1回ガード。python 失敗でも stamp 書込 (起動ごと nag 防止、WARN は1回表示)"
```

---

### Task 5: 統合検証 + レビュー + PR

- [ ] **Step 1: Full test suite**

Run: `uv run pytest scripts/runtime/tech-researcher/tests/ -v`
Expected: test_aggregate.py / test_sources.py / test_trends_select.py 全て PASS（回帰なし）

- [ ] **Step 2: 全導線のライブ確認**

```bash
task trends
rm -f ~/.cache/tech-researcher/digest-shown-*; zsh -ic 'true' 2>&1 | head -15
```
Expected: 両導線とも実 ledger の記事が URL 付きで表示される

- [ ] **Step 3: /review (Codex Review Gate 含む)**

変更全体（trends_select.py + tests + Taskfile + zsh snippet）に `/review` skill を実行。NEEDS_FIX なら修正して再レビュー。ハーネスファイル変更を含むため PASS 後に harness_review_flag を書く:

```bash
python3 "$HOME/.claude/scripts/lib/harness_review_flag.py" write
```

- [ ] **Step 4: Push + PR**

```bash
git push -u origin docs/knowledge-intake-pipeline
gh pr create --base master --title "✨ feat(trends): SP0 消費層 — task trends + zsh first-open digest (design doc 同梱)" --body "(design doc §1-6 要約 + 撤退条件 §9 + Phase 2 は別プランの旨を記載)"
```

PR body には必ず含める: (a) tech-researcher 下流断線の解消であること、(b) 撤退条件（2週間未使用なら縮退、trends-usage.log と stamp が評価データ）、(c) Phase 2（朝 Discord push / 朝 wake）は使用実績ゲート + pmset sudo 検証後の別プラン。

---

## Out of scope（このプランでやらないこと）

- **Phase 2**（朝の固定時刻 Discord push、朝 wake 再arm、nightly-wake.env への NIGHTLY_MORNING_* 追記、notify-discord の editorial 関数）— design §6.3/§6.4。使用実績ゲート通過後に別プラン。
- SP1〜SP5（配線監査統合 / PREP 自動化 / fast gate / INTEGRATE / LEARN）— design §5 roadmap。
- 既読の永続管理、embedding/RAG、新 DB — design §4 で明示的スコープ外。
