# Playbook Injection: セッション間学習連続性の強化

## 背景

バイラル CLAUDE.md の「Self-Improvement Loop」（`tasks/lessons.md` + `tasks/todo.md`）パターンの分析から、
現行 AutoEvolve システムに「学んだことを次のセッションに即座にフィードバックする最後の1マイル」が
欠けていることが判明した。

現状: `session-learner.py` が `playbooks/{project}.md` を生成しているが、`session-load.js` がそれを読んでいない。
学習データは JSONL 経由で注入されるが、キュレーション済みの人間可読な教訓は注入されない。

## 目的

1. セッション間の学習連続性を確立する（playbook → SessionStart 注入）
2. 重要な教訓を即座に永続化する（Hot Lessons）
3. 人間が編集可能なプロジェクト規約を管理する（conventions.md）

## アプローチ: 段階的デリバリー（3フェーズ）

各フェーズが独立して動作し、段階的にリリースする。

---

## ストレージ構造

```
~/.claude/agent-memory/playbooks/
└── {git-root-basename}/
    ├── hot-lessons.md        # 自動生成（emit_event + session-learner）
    ├── error-patterns.md     # 自動生成（session-learner）
    └── conventions.md        # 人間 + continuous-learning スキル
```

### ファイルの性格

| ファイル | 信頼度 | 書き手 | 寿命 | 淘汰 |
|---|---|---|---|---|
| `hot-lessons.md` | 低（未検証） | `emit_event()` 自動 | 短（15件ローテーション） | 3回未満 → 自動削除 |
| `error-patterns.md` | 中（3回以上出現） | `session-learner.py` 昇格 | 中（50件上限） | 30日再発なし → `/improve` が提案 |
| `conventions.md` | 高（人間承認済み） | 人間 / continuous-learning | 長（明示的に削除するまで） | 人間判断 |

### ファネル構造（取捨選択）

```
hot-lessons.md (受信箱: 最新15件)
    ↓ ローテーション時に判定
    ├─ 同パターン 3回以上 → error-patterns.md に昇格
    ├─ 1-2回のみ → アーカイブ（静かに削除）
    └─ 手動で conventions.md に移動も可能

error-patterns.md (実証済みパターン: 上限50件)
    ↓ /improve (Garden phase) が定期レビュー
    ├─ 5回以上 + 複数プロジェクト → MEMORY.md 昇格提案
    ├─ 30日以上再発なし → アーカイブ提案
    └─ 手動で conventions.md に移動も可能

conventions.md (人間が承認した教訓: 制限なし)
    ※ SessionStart で注入される最も信頼度の高い情報
```

### プロジェクト識別

```
1. git rev-parse --show-toplevel → basename
2. 失敗なら Path(cwd).name にフォールバック
3. 結果が空 or "." なら "unknown" → playbook 操作をスキップ
```

Python 側は `@functools.lru_cache` でセッション内キャッシュ。

---

## データフロー（全フェーズ完成後）

```
[セッション中]
  hook発火 → emit_event()
    ├─ current-session.jsonl に追記（既存）
    └─ importance >= 0.8 なら hot-lessons.md に即時追記 [P2]

[セッション終了]
  session-learner.py
    ├─ learnings/*.jsonl に永続化（既存）
    ├─ error-patterns.md に蓄積 [P1]
    └─ hot-lessons.md をローテーション（最新15件、ファネル判定） [P2]

[次のセッション開始]
  session-load.js
    ├─ loadState()（既存: 前セッション状態）
    ├─ loadPlaybook() [P1]
    │   ├─ hot-lessons.md → 最新10行を注入
    │   └─ conventions.md → 全文を注入（30行超は truncate）
    └─ loadLearningsForProfile()（既存: JSONL task-aware）
```

### loadLearningsForProfile() との共存

- `loadLearningsForProfile()`: JSONL から「今のタスクに関連する学習」（task-aware キーワードマッチ）
- `loadPlaybook()`: playbook から「このプロジェクトの一般的な教訓」
- 役割が異なるため共存する。重複はあり得るが観点が違う。

---

## Phase 1: Playbook 基盤 + SessionStart 注入

### 変更ファイル

| ファイル | 変更内容 |
|---|---|
| `scripts/learner/session-learner.py` | `_update_playbook()` → `_update_error_patterns()` リネーム。出力先を `playbooks/{project}/error-patterns.md` に変更。`_get_project_name()` 追加 |
| `scripts/runtime/session-load.js` | `loadPlaybook()` 関数追加。`getProjectName()` 追加 |

### session-learner.py

- `_get_project_name()`: git root basename、フォールバック cwd basename
- `_get_playbook_dir(project)`: `get_data_dir() / "playbooks" / project`、unknown なら None
- `_update_error_patterns()`: 旧 `_update_playbook()` のリネーム。出力先を `playbooks/{project}/error-patterns.md` に変更
- 100行上限は維持

### session-load.js

- `getProjectName()`: `git rev-parse --show-toplevel` の basename、3秒タイムアウト
- `loadPlaybook()`:
  - `hot-lessons.md` → 最新10行を stderr に出力
  - `conventions.md` → 全文（30行超は最新30行 + 警告）を stderr に出力
  - フル参照先を案内: `(Full: ~/.claude/agent-memory/playbooks/{project}/)`
- 呼び出し順: `loadState()` → `loadPlaybook()` → `loadLearningsForProfile()`

---

## Phase 2: Hot Lessons（emit_event 即時書き込み）

### 変更ファイル

| ファイル | 変更内容 |
|---|---|
| `scripts/lib/session_events.py` | `_append_hot_lesson()` 追加。`emit_event()` に閾値チェック追加 |
| `scripts/learner/session-learner.py` | `_rotate_hot_lessons()` 追加。ファネル判定ロジック |

### session_events.py

- `HOT_LESSON_THRESHOLD = 0.8`
- `_append_hot_lesson(category, data, importance)`:
  - `_get_project_name()` でプロジェクト特定
  - `playbooks/{project}/hot-lessons.md` に `- [{date}] {category} [i={importance}]: {msg[:150]}` を追記
  - 全 Exception を silent ignore（セッションを止めない）
- `emit_event()` の末尾で `if importance >= HOT_LESSON_THRESHOLD: _append_hot_lesson(...)` を呼び出し

### session-learner.py

- `_rotate_hot_lessons(project, logger)`:
  - hot-lessons.md が15件超なら overflow を処理
  - `_extract_pattern(line)`: カテゴリ + メッセージ先頭50文字でパターン抽出
  - 同パターン3回以上 → `error-patterns.md` に昇格
  - 3回未満 → アーカイブ（削除）
  - 残り15件を hot-lessons.md に書き戻し
- `process_session()` の末尾で呼び出し

---

## Phase 3: conventions.md ブートストラップ + continuous-learning 統合

### 変更ファイル

| ファイル | 変更内容 |
|---|---|
| `skills/continuous-learning/SKILL.md` | 記録先に conventions.md を追加。判定フロー更新 |

### continuous-learning スキル

記録先の判断を更新:

```
プロジェクト固有の規約？
  ├─ Yes → ~/.claude/agent-memory/playbooks/{project}/conventions.md
  │        フォーマット: "- {カテゴリ}: {内容} ({理由})"
  └─ No  → MEMORY.md（グローバル）
```

判定基準: 「3プロジェクト以上で共通 → MEMORY.md」「このプロジェクトだけ → conventions.md」

### conventions.md のブートストラップ

自動作成しない。以下のいずれかで初めて生成:

1. continuous-learning スキル発動時
2. 人間が手動作成
3. `/improve` Garden phase の昇格提案時

---

## リスク

| # | リスク | 深刻度 | 対策 | Phase |
|---|---|---|---|---|
| R1 | `emit_event()` の副作用増加でパフォーマンス劣化 | 中 | importance >= 0.8 は稀。失敗は silent | P2 |
| R2 | hot-lessons.md の無思考な肥大化 | 中 | ファネル構造: 3回未満→削除、3回以上→昇格、15件ローテーション | P2 |
| R3 | playbook 注入と loadLearningsForProfile の情報重複 | 低 | 役割分離: playbook=プロジェクト一般、JSONL=タスク関連 | P1 |
| R4 | プロジェクト名の衝突 | 低 | git root basename。衝突時は教訓が混ざるだけで破壊的ではない | P1 |
| R5 | conventions.md と MEMORY.md の境界曖昧化 | 低 | continuous-learning に判定基準を明示 | P3 |
| R6 | SessionStart のトークン消費増加 | 低 | hot-lessons 10行 + conventions 30行上限 + フル参照案内 | P1 |
| R7 | git コマンド実行のタイムアウト | 低 | 3秒タイムアウト + cwd フォールバック + lru_cache | P1 |

## 成功基準

| # | 基準 | 検証方法 |
|---|---|---|
| S1 | SessionStart で playbook が注入される | session-load.js テスト: playbook ディレクトリにファイル配置→stderr 確認 |
| S2 | importance >= 0.8 のイベントが hot-lessons.md に即時記録される | emit_event() テスト: 高 importance イベント→ファイル存在確認 |
| S3 | セッション終了時に hot-lessons.md が15件にローテーションされる | session-learner.py テスト |
| S4 | 3回未満のパターンはローテーション時に削除される | ファネルロジックのテスト |
| S5 | 既存の learnings パイプラインが壊れない | 既存テスト通過 |
| S6 | conventions.md の変更が次セッションで注入される | 手動テスト |

## テスト戦略

- P1: `test_session_learner.py` に `test_update_error_patterns_directory_structure` 追加
- P2: `test_session_events.py` に `test_hot_lesson_threshold`, `test_hot_lesson_silent_failure` 追加
- P2: `test_session_learner.py` に `test_rotate_hot_lessons`, `test_funnel_promotion` 追加
- P3: continuous-learning スキルは手動検証
