# Self-Improving Skills 設計

cognee-skills の Observe → Inspect → Amend → Evaluate ループを、
既存の AutoEvolve パイプラインに統合する。

## 設計決定

| ステップ | 決定 | 理由 |
|---------|------|------|
| Observe データ収集 | ハイブリッド (Hook + スキル内補完) | Hook でスキル呼び出しを確実に捕捉、品質判定はスキルコンテキストで補完 |
| Inspect トリガー | `/improve` に統合 | 既存 AutoEvolve ループに自然に統合、experiment_tracker と連携しやすい |
| Amend 自動化 | diff 提案まで (autoevolve/* ブランチ) | 既存の安全機構を再利用、人間レビュー必須 |
| 成功/失敗 判定 | 複合シグナル (重み付けスコア) | 既存 session_events のデータをスキル単位で集約するだけ |
| 実装順序 | 全部同時 | 手動テストデータで動作確認 |
| アプローチ | 既存基盤拡張型 | KISS/YAGNI、新規ファイル最小限 |

## Observe（スキル実行追跡）

### Hook レイヤー

**新規ファイル**: `scripts/policy/skill-tracker.py`
**イベント**: PostToolUse (Skill tool)

Skill tool が呼ばれた時点でスキル名・タイムスタンプを自動記録。
`tool_name == "Skill"` の場合のみ発火。スキル名は `input.skill` から取得。

### session_events.py 拡張

```python
def emit_skill_event(event_type: str, data: dict) -> None:
    """スキルライフサイクルイベントを記録する。

    event_type: "invocation" | "outcome"
    data には skill_name を必須で含む。
    → learnings/skill-executions.jsonl に追記
    """

def compute_skill_score(session_events: list[dict], skill_name: str) -> float:
    """セッション中のイベントからスキルの複合スコアを計算する。

    base = 0.5
    + 0.3 (ユーザーが修正なく次に進んだ)
    + 0.5 (タスク正常完了)
    - 0.3 (エラー発生)
    - 0.5 (テスト失敗)
    - 0.2/件 (レビュー Critical/Important)
    - 0.1/件 (GP違反)
    → clamp(0.0, 1.0)
    """
```

### session-learner.py 拡張

セッション終了時のフラッシュで、スキル実行データを集約:

```python
skill_invocations = [e for e in events if e.get("type") == "skill_invocation"]
for inv in skill_invocations:
    score = compute_skill_score(events, inv["skill_name"])
    append_to_learnings("skill-executions", {
        "skill_name": inv["skill_name"],
        "score": score,
        "error_count": ...,
        "gp_violations": ...,
        "review_criticals": ...,
        "test_passed": ...,
    })
```

### データスキーマ — skill-executions.jsonl

```json
{
    "timestamp": "2026-03-13T10:30:00Z",
    "skill_name": "review",
    "score": 0.7,
    "error_count": 0,
    "gp_violations": 1,
    "review_criticals": 0,
    "test_passed": true,
    "session_id": "abc123"
}
```

2系統のデータ:
- `skill-benchmarks.jsonl` — A/B テスト結果 (skill-audit 経由)
- `skill-executions.jsonl` — 実行時パフォーマンス (自動収集)

---

## Inspect（スキル劣化検知）

### autoevolve-core Analyze フェーズ拡張

既存の4カテゴリ + 新規 skills カテゴリ:

```
Phase 1: Analyze
├── errors, quality, agents, patterns (既存)
└── skills (新規) ← skill-executions.jsonl + skill-benchmarks.jsonl
```

### 分析ロジック

**a) トレンド分析** — スキルごとに直近10回の score 推移を計算

**b) 閾値判定** — 3段階の健全性分類

| 状態 | 条件 | アクション |
|------|------|-----------|
| Healthy | 平均 score >= 0.6 | 記録のみ |
| Degraded | 平均 score 0.4-0.6、または前期比 -0.1 以上の低下 | 改善候補としてフラグ |
| Failing | 平均 score < 0.4、または直近5回中4回以上失敗 | Amend 対象 |

**c) 失敗パターン特定** — Degraded/Failing スキルについて紐づくイベントを分析

**d) クロスデータ相関** — skill-executions と skill-benchmarks の突き合わせ:
- A/B retire + 実行スコア低 → 強い改善/削除根拠
- A/B keep + 実行スコア低 → 環境変化による劣化の可能性
- 実行データなし → 不要スキル候補

### 出力

`insights/analysis-YYYY-MM-DD.md` にスキル健全性セクションを追加:

```markdown
## スキル健全性分析

### Failing (要改善)
- **search-first** — score: 0.35, 傾向: 劣化(-0.25)
  - 失敗パターン: 過度な検索強制
  - A/B delta: -2.0 (retire推奨)

### Degraded (監視)
- **react-expert** — score: 0.52, 傾向: 低下(-0.13)

### Healthy
- senior-frontend (0.85), review (0.82), ...
```

---

## Amend（SKILL.md 改善提案）

### Improve フェーズ拡張

改善候補の優先度テーブルにスキル改善を追加:

| 優先度 | 条件 | アクション |
|--------|------|-----------|
| 高 | スキル Failing + 実行5回以上 | SKILL.md 修正案をブランチに作成 |
| 中 | スキル Degraded + トレンド低下 | SKILL.md 修正案をブランチに作成 |
| 低 | 実行5回未満 | 記録のみ、データ不足 |

### 修正案生成プロセス

```
1. 現在の SKILL.md を読む
2. insights の失敗パターン分析結果を参照
3. skill-benchmarks.jsonl の A/B データを参照
4. 失敗パターン → 修正アクション:
   - トリガー過剰 → description の条件を絞る
   - トリガー不足 → description にキーワード追加
   - instruction で失敗多発 → ステップの書き換え/条件追加
   - 環境変化 → ツール参照の更新
   - ベースモデルで十分 → retire 提案
5. autoevolve/YYYY-MM-DD-skill-{name} ブランチにコミット
```

### 安全制約

既存 improve-policy.md の制約 + 追加:
- 実行5回以上が改善提案の最低条件
- retire 提案時はまず `[DEPRECATED]` 付与、次回 audit で改善なければ削除提案
- 改善前の SKILL.md は git 履歴に残す

### 効果測定

既存 experiment_tracker.py を再利用:
- ブランチ作成時に `record --category skills`
- merge 後に `measure` で skill-executions.jsonl の前後7日比較
- 20%以上改善 → keep, 悪化 → revert 提案

---

## 変更対象ファイル

| ファイル | 変更種別 | 内容 |
|---------|---------|------|
| `scripts/policy/skill-tracker.py` | 新規 | PostToolUse hook でスキル呼び出し検出 |
| `scripts/lib/session_events.py` | 拡張 | `emit_skill_event()`, `compute_skill_score()` 追加 |
| `scripts/learner/session-learner.py` | 拡張 | スキル集計ロジック追加 |
| `settings.json` | 拡張 | PostToolUse に skill-tracker.py 登録 |
| `agents/autoevolve-core.md` | 拡張 | Analyze に skills カテゴリ、Improve にスキル改善ルール追加 |
| `skills/improve/SKILL.md` | 拡張 | スキル分析ステップ追加 |
| `references/improve-policy.md` | 拡張 | スキル改善の制約・閾値追加 |
