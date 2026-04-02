# Governance Map — ガバナンス俯瞰図

> Constitution 的一元管理: 全ガバナンス hooks のカテゴリマッピングと累積リスク概念。
> Source: AutoHarness (aiming-lab/AutoHarness) の9リスクカテゴリ分類を参考。

## リスクカテゴリ × 既存 Hook マッピング

| カテゴリ | リスクレベル | 担当 Hook / 仕組み | カバー状況 |
|---------|------------|-------------------|-----------|
| **危険シェルコマンド** (rm -rf, mkfs, dd) | Critical | CC 本体 bashSecurity (22種) + `docker-safety.py` | 完全 |
| **シークレット検出** (API key, token, password) | Critical | `prompt-injection-detector.py` (部分), Lefthook pre-commit | 部分的 — output 側の検出なし |
| **パス走査・改ざん** (../, symlink attack) | High | `protect-linter-config.py`, `tool-scope-enforcer.py` | 完全 |
| **ネットワーク流出** (curl\|bash, reverse shell) | Critical | CC 本体 bashSecurity | 完全 |
| **権限昇格** (sudo, chmod 777) | High | CC 本体 bashSecurity | 完全 |
| **設定改ざん** (.eslintrc, CI config) | Medium | `protect-linter-config.py` | 完全 |
| **データ破壊** (DROP TABLE, TRUNCATE) | High | CC 本体 permission system (ask) | 部分的 — DB 操作の明示的検出なし |
| **認証情報アクセス** (~/.ssh, .env) | High | `user-input-guard.py`, CC bashSecurity | 完全 |
| **コードインジェクション** (eval, exec) | Medium | `prompt-injection-detector.py` | 部分的 — Python/JS の動的実行は未検出 |

### ギャップ（将来改善候補）

- **Output 側シークレットスキャン**: ツール実行結果に含まれるシークレットの検出（PostToolUse で実装可能）
- **DB 破壊操作検出**: DROP/TRUNCATE を PreToolUse:Bash で検出する専用パターン
- **動的コード実行検出**: eval()/exec() パターンの Write/Edit 時検出

## 累積リスクスコアリング概念

AutoHarness の Turn Governor は、個別ツールコールのリスクを重み付き累積で追跡する:

```
Risk Weights: low=1, medium=3, high=10, critical=50
Threshold: 累積 100 超過でセッション警告
```

**現状の対応**: doom-loop 検出（同一ツール5回繰り返し）が部分的にカバー。
ただしリスク重みの累積追跡は行っていない。

**実装方針**: session-trace-store.py の trace エントリに `risk_level` を付与し、
`/improve` の分析フェーズでセッション単位のリスク傾向を検出可能にする。
リアルタイム閾値ブロックは CC の hook アーキテクチャ（各 hook が独立プロセス）では
共有状態のコストが高いため、事後分析アプローチを採用する。

## ガバナンス階層

```
Layer 1: CC 本体          — bashSecurity, permission system, compaction
Layer 2: CLAUDE.md        — instruction-based governance (core_principles, ワークフロー)
Layer 3: settings.json    — hook-based governance (PreToolUse, PostToolUse)
Layer 4: references/      — knowledge-based governance (このファイル, workflow-guide, etc.)
Layer 5: /improve         — 事後分析 governance (trace 分析, lessons-learned)
```

宣言的ガバナンス (AutoHarness の Constitution) に対し、
我々は **Progressive Disclosure 型ガバナンス** を採用:
- Layer 1-2 は常時アクティブ（低コスト）
- Layer 3 は条件トリガー（hook 発火時のみ）
- Layer 4-5 は必要時参照（コンテキストコスト最小）

## 関連ファイル

- `docs/agent-harness-contract.md` — Hook 4層アーキテクチャ
- `references/resource-bounds.md` — トークン予算・サーキットブレーカー
- `references/agency-safety-framework.md` — マルチエージェント安全性
- `references/failure-taxonomy.md` — 障害分類と対応
