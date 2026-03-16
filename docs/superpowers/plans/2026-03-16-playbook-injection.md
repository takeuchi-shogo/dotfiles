# Playbook Injection Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** セッション間の学習連続性を確立し、重要な教訓を即時永続化 + 次セッションで自動注入する

**Architecture:** `emit_event()` に Hot Lessons 即時書き込みを追加、`session-learner.py` の playbook 出力先をディレクトリ構造に変更、`session-load.js` に playbook 注入関数を追加。3フェーズで段階的にデリバリー。

**Tech Stack:** Python 3 (session_events.py, session-learner.py), Node.js (session-load.js), pytest

**Spec:** `docs/superpowers/specs/2026-03-16-playbook-injection-design.md`

---

## File Structure

| File | Action | Responsibility |
|---|---|---|
| `.config/claude/scripts/lib/session_events.py` | Modify | Hot Lessons 即時書き込み (`_append_hot_lesson`, `_get_project_name`) |
| `.config/claude/scripts/learner/session-learner.py` | Modify | playbook ディレクトリ出力、ローテーション、ファネル判定 |
| `.config/claude/scripts/runtime/session-load.js` | Modify | playbook 注入 (`loadPlaybook`, `getProjectName`) |
| `.config/claude/scripts/tests/test_session_events.py` | Modify | Hot Lessons テスト追加 |
| `.config/claude/scripts/tests/test_session_learner.py` | Modify | error-patterns, ローテーション、ファネルテスト追加 |
| `.config/claude/skills/continuous-learning/SKILL.md` | Modify | conventions.md 記録先追加 |

---

## Chunk 1: Phase 1 — Playbook 基盤 + SessionStart 注入

### Task 1: session-learner.py に _get_project_name() と _get_playbook_dir() を追加

**Files:**
- Modify: `.config/claude/scripts/learner/session-learner.py:1-15` (imports)
- Modify: `.config/claude/scripts/learner/session-learner.py:70` (新関数挿入)
- Test: `.config/claude/scripts/tests/test_session_learner.py`

- [ ] **Step 1: Write the failing test**

`test_session_learner.py` に追加:

```python
def test_get_project_name_returns_cwd_basename(self):
    learner = import_module("session-learner")
    name = learner._get_project_name(fallback_cwd=self.tmpdir)
    expected = Path(self.tmpdir).name
    self.assertEqual(name, expected)

def test_get_playbook_dir_creates_directory(self):
    learner = import_module("session-learner")
    d = learner._get_playbook_dir("test-project")
    self.assertTrue(d.exists())
    self.assertTrue(d.is_dir())
    self.assertEqual(d.name, "test-project")

def test_get_playbook_dir_returns_none_for_unknown(self):
    learner = import_module("session-learner")
    d = learner._get_playbook_dir("unknown")
    self.assertIsNone(d)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd .config/claude/scripts && python3 -m pytest tests/test_session_learner.py -v -k "project_name or playbook_dir"`
Expected: FAIL — `_get_project_name` not found

- [ ] **Step 3: Implement _get_project_name() and _get_playbook_dir()**

`session-learner.py` の imports に `subprocess` を追加し、`_update_playbook` の直前（行70付近）に挿入:

```python
def _get_project_name(fallback_cwd: str | None = None) -> str:
    """git root の basename を返す。git 外は cwd の basename。"""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=3,
        )
        if result.returncode == 0 and result.stdout.strip():
            return Path(result.stdout.strip()).name
    except Exception:
        pass
    cwd = fallback_cwd or os.getcwd()
    name = Path(cwd).name
    return name if name and name != "." else "unknown"


def _get_playbook_dir(project: str) -> Path | None:
    """playbook ディレクトリを返す。project が unknown なら None。"""
    if project == "unknown":
        return None
    from storage import get_data_dir
    d = get_data_dir() / "playbooks" / project
    d.mkdir(parents=True, exist_ok=True)
    return d
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd .config/claude/scripts && python3 -m pytest tests/test_session_learner.py -v -k "project_name or playbook_dir"`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add .config/claude/scripts/learner/session-learner.py .config/claude/scripts/tests/test_session_learner.py
git commit -m "✨ feat: add _get_project_name and _get_playbook_dir to session-learner"
```

---

### Task 2: _update_playbook() → _update_error_patterns() リネーム + ディレクトリ出力

**Files:**
- Modify: `.config/claude/scripts/learner/session-learner.py:71-131` (`_update_playbook`)
- Modify: `.config/claude/scripts/learner/session-learner.py:357` (呼び出し箇所)
- Test: `.config/claude/scripts/tests/test_session_learner.py`

- [ ] **Step 1: Write the failing test**

```python
def test_update_error_patterns_creates_directory_structure(self):
    from session_events import emit_event
    learner = import_module("session-learner")

    emit_event("error", {"message": "Permission denied", "command": "npm test"})
    emit_event("error", {"message": "segfault occurred", "command": "build"})
    learner.process_session(cwd=self.tmpdir)

    project = Path(self.tmpdir).name
    error_patterns_path = Path(self.tmpdir) / "playbooks" / project / "error-patterns.md"
    self.assertTrue(error_patterns_path.exists())
    content = error_patterns_path.read_text()
    self.assertIn("Error:", content)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd .config/claude/scripts && python3 -m pytest tests/test_session_learner.py::TestSessionLearnerScoring::test_update_error_patterns_creates_directory_structure -v`
Expected: FAIL — `error-patterns.md` not found (旧コードは `playbooks/{project}.md` に書く)

- [ ] **Step 3: Rename _update_playbook to _update_error_patterns and change output path**

`session-learner.py` を編集:

1. `_update_playbook` → `_update_error_patterns` にリネーム
2. 出力先を `playbooks/{project}/error-patterns.md` に変更:

```python
def _update_error_patterns(summary: dict, logger: logging.Logger) -> None:
    """プロジェクト固有の error patterns を更新する。"""
    from datetime import datetime, timezone

    project = summary.get("project", "unknown")
    playbook_dir = _get_playbook_dir(project)
    if playbook_dir is None or summary["total_events"] < 2:
        return

    error_patterns_path = playbook_dir / "error-patterns.md"

    entries: list[str] = []
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    for error in summary["_errors"][:3]:
        data = error.get("data", {})
        msg = data.get("message", data.get("error", ""))
        if msg:
            fix = data.get("fix", "")
            entry = f"- [{ts}] Error: {msg[:120]}"
            if fix:
                entry += f" -> Fix: {fix[:80]}"
            entries.append(entry)

    for issue in summary["_quality"][:3]:
        data = issue.get("data", {})
        rule = data.get("rule", "")
        file = data.get("file", "")
        if rule:
            name = Path(file).name if file else "unknown"
            entries.append(f"- [{ts}] {rule} violation in {name}")

    for pattern in summary["_patterns"][:2]:
        data = pattern.get("data", {})
        desc = data.get("description", data.get("pattern", ""))
        if desc:
            entries.append(f"- [{ts}] Pattern: {desc[:120]}")

    if not entries:
        return

    existing = ""
    if error_patterns_path.exists():
        existing = error_patterns_path.read_text(encoding="utf-8")
    if not existing:
        existing = f"# {project} Error Patterns\n\nAuto-accumulated from session learnings.\n\n"

    new_content = existing.rstrip() + "\n" + "\n".join(entries) + "\n"

    lines = new_content.splitlines()
    if len(lines) > 50:
        header = lines[:4]
        body = lines[4:]
        lines = header + body[-(50 - len(header)):]
        new_content = "\n".join(lines) + "\n"

    error_patterns_path.write_text(new_content, encoding="utf-8")
    logger.info("session-learner: updated error-patterns for %s", project)
```

3. `process_session()` 内の呼び出しを更新（行357）:

```python
    _update_error_patterns(summary, logger)
```

- [ ] **Step 4: Run all tests to verify pass + no regression**

Run: `cd .config/claude/scripts && python3 -m pytest tests/test_session_learner.py -v`
Expected: ALL PASS

- [ ] **Step 5: Commit**

```bash
git add .config/claude/scripts/learner/session-learner.py .config/claude/scripts/tests/test_session_learner.py
git commit -m "♻️ refactor: rename _update_playbook to _update_error_patterns with directory structure"
```

---

### Task 3: session-load.js に loadPlaybook() を追加

**Files:**
- Modify: `.config/claude/scripts/runtime/session-load.js:214-241`

- [ ] **Step 1: Implement getProjectName()**

`session-load.js` の `detectTools()` 関数の後に追加:

```javascript
function getProjectName() {
	try {
		const toplevel = execSync("git rev-parse --show-toplevel 2>/dev/null", {
			timeout: 3000,
			encoding: "utf8",
		}).trim();
		if (toplevel) return path.basename(toplevel);
	} catch {
		// Not a git repo — fallback
	}
	const name = path.basename(process.cwd());
	return name && name !== "." ? name : null;
}
```

- [ ] **Step 2: Implement loadPlaybook()**

`getProjectName()` の後に追加:

```javascript
function loadPlaybook() {
	const project = getProjectName();
	if (!project) return;

	const dataDir =
		process.env.AUTOEVOLVE_DATA_DIR ||
		path.join(process.env.HOME, ".claude", "agent-memory");
	const playbookDir = path.join(dataDir, "playbooks", project);
	if (!fs.existsSync(playbookDir)) return;

	const lines = [];

	// hot-lessons.md: 最新10行
	const hotPath = path.join(playbookDir, "hot-lessons.md");
	if (fs.existsSync(hotPath)) {
		try {
			const content = fs
				.readFileSync(hotPath, "utf8")
				.trim()
				.split("\n")
				.filter(Boolean);
			const recent = content.slice(-10);
			if (recent.length > 0) {
				lines.push(
					`[Playbook: ${project}] Hot lessons (${recent.length}件):`,
				);
				recent.forEach((l) => lines.push(`  ${l}`));
			}
		} catch {
			/* skip unreadable files */
		}
	}

	// conventions.md: 全文（30行超は truncate）
	const convPath = path.join(playbookDir, "conventions.md");
	if (fs.existsSync(convPath)) {
		try {
			const content = fs.readFileSync(convPath, "utf8").trim();
			if (content) {
				const convLines = content.split("\n");
				lines.push(`[Playbook: ${project}] Conventions:`);
				if (convLines.length > 30) {
					convLines
						.slice(-30)
						.forEach((l) => lines.push(`  ${l}`));
					lines.push(
						`  (${convLines.length}行中30行のみ表示。Read で全文参照可)`,
					);
				} else {
					convLines.forEach((l) => lines.push(`  ${l}`));
				}
			}
		} catch {
			/* skip unreadable files */
		}
	}

	if (lines.length > 0) {
		lines.push(`  (Full: ~/.claude/agent-memory/playbooks/${project}/)`);
		process.stderr.write(lines.join("\n") + "\n");
	}
}
```

- [ ] **Step 3: Update call order in stdin handler**

`session-load.js` の末尾の `process.stdin.on("end", ...)` を変更:

```javascript
process.stdin.on("end", () => {
	loadState();
	loadPlaybook(); // ← 追加

	// Load profile from last checkpoint or task-aware
	let profile = "task-aware";
	try {
		const cpPath = path.join(
			process.env.HOME,
			".claude",
			"session-state",
			"last-checkpoint.json",
		);
		if (fs.existsSync(cpPath)) {
			const cp = JSON.parse(fs.readFileSync(cpPath, "utf8"));
			profile = cp.active_profile || "default";
		}
	} catch {
		/* ignore */
	}

	loadLearningsForProfile(profile);
	process.stdout.write(data);
});
```

- [ ] **Step 4: Manual integration test**

手動テスト:

```bash
# テスト用 playbook を作成
PROJECT=$(basename $(git rev-parse --show-toplevel))
mkdir -p ~/.claude/agent-memory/playbooks/$PROJECT
echo "- [2026-03-16] error [i=0.9]: test hot lesson" > ~/.claude/agent-memory/playbooks/$PROJECT/hot-lessons.md
echo "- convention: use bun instead of npm" > ~/.claude/agent-memory/playbooks/$PROJECT/conventions.md

# session-load.js を直接実行して stderr を確認
echo '{}' | node ~/.claude/scripts/runtime/session-load.js 2>&1 1>/dev/null | grep "Playbook"

# クリーンアップ
rm -rf ~/.claude/agent-memory/playbooks/$PROJECT
```

Expected: `[Playbook: dotfiles] Hot lessons` と `[Playbook: dotfiles] Conventions` が表示される

- [ ] **Step 5: Commit**

```bash
git add .config/claude/scripts/runtime/session-load.js
git commit -m "✨ feat: add playbook injection to SessionStart"
```

---

## Chunk 2: Phase 2 — Hot Lessons (emit_event 即時書き込み)

### Task 4: session_events.py に _get_project_name() と _append_hot_lesson() を追加

**Files:**
- Modify: `.config/claude/scripts/lib/session_events.py:1-10` (imports)
- Modify: `.config/claude/scripts/lib/session_events.py:117-150` (emit_event)
- Test: `.config/claude/scripts/tests/test_session_events.py`

- [ ] **Step 1: Write the failing tests**

`test_session_events.py` に追加:

```python
class TestHotLessons:
    """Hot Lessons 即時書き込みのテスト。"""

    def test_high_importance_creates_hot_lesson(self, isolate_data_dir):
        emit_event("error", {"message": "Permission denied", "command": "npm test"})
        project_dir = isolate_data_dir / "playbooks"
        # プロジェクト名は git root or cwd — テスト環境では cwd のフォールバック
        hot_files = list(project_dir.rglob("hot-lessons.md"))
        assert len(hot_files) >= 1
        content = hot_files[0].read_text()
        assert "Permission denied" in content
        assert "[i=" in content

    def test_low_importance_skips_hot_lesson(self, isolate_data_dir):
        emit_event("error", {"message": "warning: unused var", "command": "lint"})
        project_dir = isolate_data_dir / "playbooks"
        hot_files = list(project_dir.rglob("hot-lessons.md"))
        # low importance (0.2) は hot lesson にならない
        if hot_files:
            content = hot_files[0].read_text()
            assert "unused var" not in content

    def test_hot_lesson_silent_failure(self, isolate_data_dir, monkeypatch):
        """playbook 書き込み失敗でも emit_event は成功する。"""
        import session_events
        monkeypatch.setattr(session_events, "_append_hot_lesson", lambda *a, **k: (_ for _ in ()).throw(OSError("disk full")))
        # Should not raise
        emit_event("error", {"message": "segfault occurred"})
        events = flush_session()
        assert len(events) == 1
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd .config/claude/scripts && python3 -m pytest tests/test_session_events.py::TestHotLessons -v`
Expected: FAIL — `TestHotLessons` tests fail (no hot-lessons.md created)

- [ ] **Step 3: Implement _get_project_name() and _append_hot_lesson()**

`session_events.py` に追加。imports セクションに `subprocess`, `functools` を追加:

```python
import functools
import subprocess
```

`emit_event()` の前に新関数を追加:

```python
HOT_LESSON_THRESHOLD = 0.8


@functools.lru_cache(maxsize=1)
def _get_project_name() -> str:
    """git root の basename を返す。git 外は cwd の basename。"""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=3,
        )
        if result.returncode == 0 and result.stdout.strip():
            return Path(result.stdout.strip()).name
    except Exception:
        pass
    name = Path.cwd().name
    return name if name and name != "." else "unknown"


def _append_hot_lesson(category: str, data: dict, importance: float) -> None:
    """importance >= threshold のイベントを hot-lessons.md に即時追記する。"""
    try:
        project = _get_project_name()
        if project == "unknown":
            return
        playbook_dir = _get_data_dir() / "playbooks" / project
        playbook_dir.mkdir(parents=True, exist_ok=True)
        hot_path = playbook_dir / "hot-lessons.md"

        msg = data.get("message", data.get("rule", data.get("detail", "")))
        if not msg:
            return

        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        line = f"- [{ts}] {category} [i={importance}]: {str(msg)[:150]}\n"

        with open(hot_path, "a", encoding="utf-8") as f:
            f.write(line)
    except Exception:
        pass  # hot lesson 書き込み失敗はセッションを止めない
```

- [ ] **Step 4: Add hot lesson call to emit_event()**

`emit_event()` の末尾（行144の `logger.debug(...)` の後、`except` の前）に追加:

```python
        # Hot Lessons: 重要度が高いイベントは即座に playbook に記録
        if importance >= HOT_LESSON_THRESHOLD:
            try:
                _append_hot_lesson(category, data, importance)
            except Exception:
                pass
```

- [ ] **Step 5: Run tests to verify pass**

Run: `cd .config/claude/scripts && python3 -m pytest tests/test_session_events.py -v`
Expected: ALL PASS (新テスト + 既存テスト)

- [ ] **Step 6: Commit**

```bash
git add .config/claude/scripts/lib/session_events.py .config/claude/scripts/tests/test_session_events.py
git commit -m "✨ feat: add Hot Lessons immediate write to emit_event"
```

---

### Task 5: session-learner.py に _rotate_hot_lessons() とファネル判定を追加

**Files:**
- Modify: `.config/claude/scripts/learner/session-learner.py`
- Test: `.config/claude/scripts/tests/test_session_learner.py`

- [ ] **Step 1: Write the failing tests**

```python
def test_rotate_hot_lessons_keeps_15(self):
    learner = import_module("session-learner")
    project = Path(self.tmpdir).name
    playbook_dir = Path(self.tmpdir) / "playbooks" / project
    playbook_dir.mkdir(parents=True)
    hot_path = playbook_dir / "hot-lessons.md"

    # 20件書き込み
    lines = [f"- [2026-03-16] error [i=0.9]: error {i}\n" for i in range(20)]
    hot_path.write_text("".join(lines))

    logger = logging.getLogger("autoevolve")
    learner._rotate_hot_lessons(project, logger)

    remaining = [l for l in hot_path.read_text().splitlines() if l.strip()]
    self.assertEqual(len(remaining), 15)

def test_funnel_promotes_repeated_patterns(self):
    learner = import_module("session-learner")
    project = Path(self.tmpdir).name
    playbook_dir = Path(self.tmpdir) / "playbooks" / project
    playbook_dir.mkdir(parents=True)
    hot_path = playbook_dir / "hot-lessons.md"

    # 同じパターンを4回 + 別パターンを16回 = 20件
    lines = [f"- [2026-03-16] error [i=0.9]: Permission denied\n" for _ in range(4)]
    lines += [f"- [2026-03-16] error [i=0.8]: unique error {i}\n" for i in range(16)]
    hot_path.write_text("".join(lines))

    logger = logging.getLogger("autoevolve")
    learner._rotate_hot_lessons(project, logger)

    # error-patterns.md に "Permission denied" が昇格
    ep_path = playbook_dir / "error-patterns.md"
    self.assertTrue(ep_path.exists())
    content = ep_path.read_text()
    self.assertIn("Permission denied", content)

def test_funnel_discards_infrequent_patterns(self):
    learner = import_module("session-learner")
    project = Path(self.tmpdir).name
    playbook_dir = Path(self.tmpdir) / "playbooks" / project
    playbook_dir.mkdir(parents=True)
    hot_path = playbook_dir / "hot-lessons.md"

    # 全て異なるパターン 20件
    lines = [f"- [2026-03-16] error [i=0.9]: unique error {i}\n" for i in range(20)]
    hot_path.write_text("".join(lines))

    logger = logging.getLogger("autoevolve")
    learner._rotate_hot_lessons(project, logger)

    # error-patterns.md は作られない（昇格対象なし）
    ep_path = playbook_dir / "error-patterns.md"
    self.assertFalse(ep_path.exists())
```

`setUp` に `import logging` を追加。

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd .config/claude/scripts && python3 -m pytest tests/test_session_learner.py -v -k "rotate or funnel"`
Expected: FAIL — `_rotate_hot_lessons` not found

- [ ] **Step 3: Implement _extract_pattern() and _rotate_hot_lessons()**

`session-learner.py` の `_update_error_patterns()` の後に追加:

```python
def _extract_pattern(line: str) -> str:
    """hot-lessons の行からパターンキーを抽出する。

    フォーマット: "- [date] category [i=X.X]: message"
    → "category:message先頭50文字" をキーにする。
    """
    import re
    m = re.match(r"- \[\d{4}-\d{2}-\d{2}\] (\w+) \[i=[\d.]+\]: (.+)", line)
    if m:
        category = m.group(1)
        msg = m.group(2)[:50].strip()
        return f"{category}:{msg}"
    return line.strip()[:60]


def _rotate_hot_lessons(project: str, logger: logging.Logger) -> None:
    """hot-lessons.md を最新15件にローテーションする。

    溢れたエントリはファネル判定:
    - 同パターン3回以上 → error-patterns.md に昇格
    - 3回未満 → アーカイブ（削除）
    """
    playbook_dir = _get_playbook_dir(project)
    if playbook_dir is None:
        return
    hot_path = playbook_dir / "hot-lessons.md"
    if not hot_path.exists():
        return

    all_lines = [l for l in hot_path.read_text("utf-8").splitlines() if l.strip()]
    if len(all_lines) <= 15:
        return

    overflow = all_lines[:-15]
    kept = all_lines[-15:]

    # ファネル判定: overflow の各行について、全行での出現回数をカウント
    from collections import Counter
    pattern_counts = Counter(_extract_pattern(l) for l in all_lines)

    promote = []
    for line in overflow:
        pattern = _extract_pattern(line)
        if pattern_counts[pattern] >= 3:
            promote.append(line)

    # 昇格対象を error-patterns.md に追記（重複除去）
    if promote:
        error_patterns_path = playbook_dir / "error-patterns.md"
        existing = ""
        if error_patterns_path.exists():
            existing = error_patterns_path.read_text(encoding="utf-8")
        if not existing:
            existing = f"# {project} Error Patterns\n\nAuto-accumulated from hot-lessons overflow.\n\n"

        # 既存の error-patterns に同じ行がないものだけ追加
        existing_lines = set(existing.splitlines())
        new_entries = [l for l in promote if l not in existing_lines]

        if new_entries:
            new_content = existing.rstrip() + "\n" + "\n".join(new_entries) + "\n"
            ep_lines = new_content.splitlines()
            if len(ep_lines) > 50:
                header = ep_lines[:4]
                body = ep_lines[4:]
                ep_lines = header + body[-(50 - len(header)):]
                new_content = "\n".join(ep_lines) + "\n"
            error_patterns_path.write_text(new_content, encoding="utf-8")

    hot_path.write_text("\n".join(kept) + "\n", "utf-8")
    archived = len(overflow) - len(promote)
    logger.info(
        "session-learner: rotated hot-lessons for %s (%d total, promoted %d, archived %d)",
        project, len(all_lines), len(promote), archived,
    )
```

- [ ] **Step 4: Add _rotate_hot_lessons() call to process_session()**

`process_session()` 内の `_update_error_patterns(summary, logger)` の後に追加:

```python
    _rotate_hot_lessons(summary["project"], logger)
```

- [ ] **Step 5: Run all tests**

Run: `cd .config/claude/scripts && python3 -m pytest tests/test_session_learner.py -v`
Expected: ALL PASS

- [ ] **Step 6: Run session_events tests too (no regression)**

Run: `cd .config/claude/scripts && python3 -m pytest tests/ -v`
Expected: ALL PASS

- [ ] **Step 7: Commit**

```bash
git add .config/claude/scripts/learner/session-learner.py .config/claude/scripts/tests/test_session_learner.py
git commit -m "✨ feat: add hot-lessons rotation with funnel promotion logic"
```

---

## Chunk 3: Phase 3 — conventions.md + continuous-learning 統合

### Task 6: continuous-learning スキルに conventions.md 記録先を追加

**Files:**
- Modify: `.config/claude/skills/continuous-learning/SKILL.md:45-62`

- [ ] **Step 1: Update the Record section**

`SKILL.md` の `### 3. Record` セクション（行45-62）を以下に差し替え:

```markdown
### 3. Record

記録先の判断:

```
プロジェクト固有の規約？
  ├─ Yes → ~/.claude/agent-memory/playbooks/{project}/conventions.md
  │        {project} = git rev-parse --show-toplevel の basename
  │        フォーマット: "- {カテゴリ}: {内容} ({理由})"
  └─ No（3プロジェクト以上で共通）
      → MEMORY.md に追記（索引として1-2行）
        → 詳細が必要なら別ファイルに分離
```

conventions.md 記録時の注意:
- ファイルが存在しなければ新規作成
- 既存エントリとの重複を確認してから追記
- 30行を超えたら古いエントリの整理を提案

MEMORY.md 記録フォーマット:

```markdown
## [分類]: [パターン名]
- **状況**: いつ発生するか
- **対処**: 何をすべきか
- **理由**: なぜそうするか（省略可）
```
```

- [ ] **Step 2: Verify SKILL.md is valid markdown**

Run: `head -20 .config/claude/skills/continuous-learning/SKILL.md`
Expected: frontmatter + content intact

- [ ] **Step 3: Commit**

```bash
git add .config/claude/skills/continuous-learning/SKILL.md
git commit -m "✨ feat: add conventions.md as recording target for continuous-learning"
```

---

### Task 7: autoevolve-core エージェントに playbook ディレクトリを入力に追加

**Files:**
- Modify: `.config/claude/agents/autoevolve-core.md:39-50` (入力データテーブル)

- [ ] **Step 1: Add playbook files to input data table**

`autoevolve-core.md` の Phase 1 入力データテーブルに追加:

```markdown
| `playbooks/{project}/error-patterns.md` | 昇格済みエラーパターン |
| `playbooks/{project}/hot-lessons.md` | 未検証の即時記録 |
| `playbooks/{project}/conventions.md` | 人間承認済み規約 |
```

- [ ] **Step 2: Add playbook review to Garden phase**

Garden phase のタスクリスト（行196-209）に追加:

```markdown
6. **Playbook レビュー**: `playbooks/*/error-patterns.md` を走査
   - 30日以上再発なしのエントリ → アーカイブ提案
   - 5回以上 + 複数プロジェクト → MEMORY.md 昇格提案
   - conventions.md と重複するエントリ → 削除提案
```

- [ ] **Step 3: Commit**

```bash
git add .config/claude/agents/autoevolve-core.md
git commit -m "✨ feat: add playbook directory as input to autoevolve-core Garden phase"
```

---

### Task 8: 全体統合テスト

- [ ] **Step 1: Run all unit tests**

Run: `cd .config/claude/scripts && python3 -m pytest tests/ -v`
Expected: ALL PASS

- [ ] **Step 2: Manual end-to-end test**

```bash
# 1. テスト用 playbook を作成
PROJECT=$(basename $(git rev-parse --show-toplevel))
mkdir -p ~/.claude/agent-memory/playbooks/$PROJECT
echo "- [2026-03-16] error [i=0.9]: test lesson" > ~/.claude/agent-memory/playbooks/$PROJECT/hot-lessons.md
echo "- convention: always use bun" > ~/.claude/agent-memory/playbooks/$PROJECT/conventions.md

# 2. session-load.js を実行して注入を確認
echo '{}' | node ~/.claude/scripts/runtime/session-load.js 2>&1 1>/dev/null

# 3. クリーンアップ
rm -rf ~/.claude/agent-memory/playbooks/$PROJECT
```

Expected: `[Playbook: dotfiles]` セクションが stderr に出力される

- [ ] **Step 3: Commit final integration state**

```bash
git commit --allow-empty -m "🔧 chore: complete playbook injection implementation (P1+P2+P3)"
```
