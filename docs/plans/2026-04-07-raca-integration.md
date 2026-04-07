# RACA 知見統合プラン

> Source: "RACA: Research Assistant Coding Agent for Ph.D. Students" ブログ記事
> Analysis: docs/research/2026-04-07-raca-harness-analysis.md
> Created: 2026-04-07
> Size: L（8項目、段階実行）

## 概要

RACA 記事から抽出した知見をソフトウェア開発ハーネスに適用する。
研究ワークフロー前提の手法を SW 開発文脈にリフレームして統合する。

## タスク一覧

### Wave 1: 高優先度（既存部品の結線） ✅

#### T1: Canary Job — 変更面ベース自動 preflight [M] ✅
- **目的**: 変更対象（auth, DB, API, migration 等）に応じた軽量検証を自動実行
- **成果物**:
  - `references/change-surface-preflight.md` — 変更面→preflight マッピング表
  - `settings.json` — PostToolUse hook で変更面検出 → 適切な preflight 起動
- **既存部品**: completion-gate.py, /validate, smoke test rule (Rule 32)
- **依存**: なし

#### T2: Red-teaming 自動起動 [M] ✅
- **目的**: 高リスク変更で edge-case-hunter / silent-failure-hunter を hook で自動トリガー
- **成果物**:
  - `settings.json` — PostToolUse hook（高リスクファイルパターン検出時に自動起動）
  - `references/high-risk-change-patterns.md` — 高リスク変更パターン定義
- **高リスクパターン例**: auth/, middleware/, migration/, *_test.go の大幅変更, external API client
- **既存部品**: edge-case-hunter agent, silent-failure-hunter agent, /edge-case-analysis skill
- **依存**: なし

#### T3: Repair Routing Table [S] ✅
- **目的**: 失敗時に references/ / rules/ / skill / hook のどこを修正すべきかの判定表
- **成果物**:
  - `references/repair-routing.md` — 障害種別→修復先レイヤーのマッピング
- **修復先レイヤー**: CLAUDE.md / references/ / rules/ / scripts/ / skills/ / agents/
- **障害種別例**: 繰り返しエラー→error-fix-guides, パイプライン違反→rules/, エージェント品質→agents/
- **既存部品**: AutoEvolve improve-policy.md のカテゴリ、session-learner.py
- **依存**: なし

### Wave 2: 中優先度（新規リファレンス + 既存強化） ✅

#### T4: Backend Task Archetype Templates [M] ✅
- **目的**: 反復性の高い SW 開発領域のリファレンスドキュメント体系化
- **成果物**:
  - `references/task-archetypes/` — 領域別テンプレート（初期は 3-5 領域）
- **初期対象領域**: auth/認証, DB migration, external API integration, validation, error handling
- **フォーマット**: タスクの定義 / 既知の落とし穴 / 不変条件 / テスト戦略 / コードスニペット
- **既存部品**: compile-wiki taxonomy, wiki INDEX, tacit-knowledge pipeline
- **依存**: T3（repair routing が archetype からの修復先を参照）

#### T5: Stage Transition 結線 [M] ✅
- **目的**: EPD パイプラインのステージ遷移を明文化・自動化
- **成果物**:
  - `references/stage-transition-rules.md` — 各ステージの完了条件と次ステージへの遷移ルール
  - 必要に応じて settings.json の hook 追加
- **既存部品**: EPD skill, completion-gate.py, golden-check.py, CLAUDE.md ワークフロー
- **依存**: T1, T2（preflight と red-team が遷移ルールに組み込まれる）

#### T6: Observability Dashboard [M] ✅
- **目的**: agent routing / 検証失敗 / 再試行の観測信号を意思決定に接続
- **成果物**:
  - `references/observability-signals.md` — 観測すべき信号とアクション定義
  - dispatch_logger の出力フォーマット標準化（必要に応じて）
- **既存部品**: dispatch_logger.sh, cmux result collection, AutoEvolve 学習ループ
- **依存**: T5（ステージ遷移の信号が observability に流れる）

### Wave 3: 低優先度（拡張）

#### T7: Conductor 統合 [M]
- **目的**: dispatch に validate/red-team の自動差し込み、subagent 間裁定を追加
- **成果物**:
  - dispatch skill の強化（stage-aware routing）
  - `references/conductor-protocol.md` — 裁定ルール
- **依存**: T1, T2, T5

#### T8: gaming-detector 拡張 [S]
- **目的**: specification gaming の検出パターン追加
- **成果物**:
  - `scripts/policy/gaming-detector.py` の検出パターン拡張
- **依存**: T3（repair routing が gaming 検出後の修復先を指定）

## 依存関係

```
Wave 1 (並列実行可能):
  T1 ─┐
  T2 ─┤
  T3 ─┘
       │
Wave 2:
  T4 ← T3
  T5 ← T1, T2
  T6 ← T5
       │
Wave 3:
  T7 ← T1, T2, T5
  T8 ← T3
```

## 実行方針

- Wave 1 の T1, T2, T3 は並列実行可能。別セッションで /rpi を使う
- Wave 2 は Wave 1 完了後に着手
- Wave 3 は Wave 2 の効果を見てから判断（下記「Wave 3 着手判断基準」参照）
- 各タスクは M 規模ワークフロー（Plan → Implement → Review → Verify）に従う
- 撤退条件: hook の追加で開発速度が低下する場合、hook を無効化して reference のみ残す

## Wave 3 着手判断基準

Wave 2 完了から **2週間後（2026-04-21 以降）** に以下を計測し、Wave 3 の着手を判断する。

### 観測指標

| 指標 | 計測方法 | Wave 3 着手の閾値 |
|------|---------|-----------------|
| Archetype 参照頻度 | repair-routing 経由で `task-archetypes/` にルーティングされたか（session-learner ログ） | 2週間で 1回以上参照 |
| Stage transition 準拠 | completion-gate の Review Gate / Comprehension Check 発火率 | 既存ゲートの false positive が増加しない |
| Observability Gap の実害 | Gap 1-2（CFS 未接続、clusters 読み手なし）が問題になったか | 「接続されていれば防げた」ケースが 1回以上発生 |

### 判断フロー

1. `/improve` を実行し、AutoEvolve がこれらのリファレンスを改善候補として拾うか確認
2. `doc-garden-check.py` で archetype の陳腐化が検出されないか確認
3. session-learner のログで CFS 後のカスケード障害を確認

### 判断マトリクス

| リファレンス利用 | Gap 実害 | アクション |
|----------------|---------|-----------|
| 使われている | あり | **Wave 3 着手**（T7 Conductor, T8 gaming-detector） |
| 使われている | なし | **Wave 3 保留**（現状で十分） |
| 使われていない | — | **Wave 2 改善が先**（内容不十分 or 参照パス断絶） |
