# Agency Safety Framework

> Bengio の Scientist AI 論文 (arXiv:2502.15657) の Agency 3本柱モデルに基づく。
> ハーネスの安全機構を体系的に整理し、新規コントロール追加時の設計指針を提供する。

## 3本柱モデル

| 柱 | 定義 | 制御方針 |
|---|---|---|
| **Affordances** | エージェントが環境に対して実行可能な操作の集合 | 制限する（できることを減らす） |
| **Goal-directedness** | 目標を持続的に追求する傾向の強さ | 制限する（暴走を防ぐ） |
| **Intelligence** | 問題解決・推論・学習の能力 | 活用する（制限しない） |

**核心原則**: 3柱すべてが高い状態は最もリスクが高い。安全なエージェントは少なくとも1柱を意図的に制限する。

---

## 現在のハーネスにおけるマッピング

### Affordances 制限（できることを減らす）

エージェントが環境に対して実行できる操作を明示的に制限する。

| コントロール | 場所 | 制限内容 |
|---|---|---|
| Bash deny rules | `settings.json` permissions.deny | `rm -rf`, `git push --force`, `git reset --hard`, `sudo`, `ssh` 等の危険コマンド |
| Read deny rules | `settings.json` permissions.deny | `.env*`, `*.pem`, `*credentials*`, `~/.ssh/**` 等の機密ファイル |
| Write deny rules | `settings.json` permissions.deny | `~/.ssh/**`, `~/.aws/**` への書き込み |
| protect-linter-config.py | `scripts/policy/` | `.eslintrc*`, `biome.json`, `.prettierrc*` 等の設定ファイル書き込みブロック |
| C-003: スコープ制約 | `references/constraints-library.md` | 指示範囲外のコード変更禁止 |
| C-004: DB 制約 | `references/constraints-library.md` | 直接 ALTER TABLE 禁止、マイグレーション必須 |
| C-007: セキュリティ制約 | `references/constraints-library.md` | シークレットのハードコード禁止 |
| docker-safety.py | `scripts/policy/` | Docker コマンドの安全性検証 |
| Depth-1 Rule | `references/subagent-delegation-guide.md` | サブエージェントがサブエージェントを生成しない |

### Goal-directedness 制限（暴走を防ぐ）

エージェントが目標を過度に追求し続けることを防ぐ。

| コントロール | 場所 | 制限内容 |
|---|---|---|
| completion-gate.py | `scripts/policy/` | テスト実行の強制 + MAX_RETRIES=2 で無限ループ防止 |
| resource-bounds.md | `references/` | Doom-loop 検出（20 fingerprints, 3 repeats）、Exploration Spiral（5 consecutive reads） |
| stagnation-detector.py | `scripts/policy/` | 同種エラー反復・連続失敗・過剰編集を検出し戦略切替を提案 |
| improve-policy Rule 17 | `references/improve-policy.md` | 連続 reject 上限（3回で停止 + エスカレーション） |
| improve-policy Rule 18 | `references/improve-policy.md` | 目的メトリクス後退検出（ベースライン下回りで停止） |
| improve-policy Rule 19 | `references/improve-policy.md` | 単一変更規律（1イテレーション1変更のみ） |
| Context Pressure Levels | `references/resource-bounds.md` | 80% Warning → 90% Critical → 95% Emergency |
| C-008: 並行実行制約 | `references/constraints-library.md` | 他エージェントのファイル変更禁止 |
| improve-policy Rule 20-22 | `references/improve-policy.md` | Specification gaming 検出（Proxy metric 乖離、自己参照改善禁止、メトリクス多様性） |

### Intelligence 活用（制限しない）

エージェントの推論・分析能力は制限せず、最大限活用する。

| コントロール | 場所 | 活用内容 |
|---|---|---|
| agent-router.py | `scripts/policy/` | タスク種別に基づく最適エージェントへの自動ルーティング |
| subagent-delegation-guide.md | `references/` | Sync/Async/Scheduled 3パターン + 5オーケストレーション |
| Codex 委譲 | `rules/codex-delegation.md` | 深い推論（設計/リスク分析/デバッグ）に gpt-5.4 を活用 |
| Gemini 委譲 | `rules/gemini-delegation.md` | 1M コンテキスト分析/外部リサーチ/マルチモーダル処理 |
| 知識蒸留パイプライン | `references/improve-policy.md` | L0→L4 の段階的知識昇格 |
| file-pattern-router.py | `scripts/policy/` | ファイル種別に基づくスペシャリスト自動選択 |

---

## 新規コントロール追加のガイドライン

新しい hook、constraint、policy を追加する際は、以下を明示すること:

### 1. どの柱を制限しているか

```markdown
## 新規コントロール: {名前}

- **柱**: Affordances / Goal-directedness / Intelligence
- **制限内容**: {具体的に何を制限するか}
- **根拠**: {なぜこの制限が必要か}
```

### 2. 制限の強度

| 強度 | 説明 | 例 |
|---|---|---|
| **Hard block** | 操作を完全に拒否（exit code 2） | deny rules, protect-linter-config |
| **Soft warning** | 警告を出すが操作は許可 | golden-check, stagnation-detector |
| **Budget limit** | 回数・リソースの上限を設ける | MAX_RETRIES, context pressure |

### 3. チェックリスト

- [ ] 既存の3柱マッピングに追加したか
- [ ] Affordances + Goal-directedness + Intelligence すべてを同時に制限していないか
- [ ] Intelligence 柱は制限していないか（制限する場合は強い根拠が必要）
- [ ] 制限の強度は適切か（過剰でも不足でもないか）
- [ ] ロールバック可能か

---

## Tool-Use Safety Taxonomy

> Nemotron-Agentic-Safety (11K labeled telemetry traces) の分類体系を参考に、
> ツール使用ワークフローにおける安全性パターンを定義する。

### 障害モード

| 障害モード | 説明 | 検出方法 | 既存コントロール |
|-----------|------|---------|----------------|
| **Tool Hallucination** | 存在しないツール名・パラメータの生成 | ツール名の allowlist 照合 | agentshield-filter.py |
| **Scope Violation** | 許可範囲外のリソースへのアクセス試行 | deny rules + パス検証 | settings.json deny rules, protect-linter-config.py |
| **Cascading Failure** | 1つのツール失敗が連鎖的に後続操作を破壊 | CFS 検出 (session-learner.py) | stagnation-detector.py, completion-gate.py |
| **Parameter Injection** | ツールパラメータへの悪意ある値の注入 | 入力サニタイズ + パターンマッチ | docker-safety.py, deny rules |
| **Excessive Autonomy** | 確認なしで高影響操作を連続実行 | 操作カウント + 影響度評価 | completion-gate.py MAX_RETRIES |
| **Silent Data Corruption** | ツール成功だが結果が不正（誤ったファイル編集等） | 差分検証 + テスト実行 | golden-check.py, completion-gate.py |

### 3本柱との対応

| 障害モード | 関連する柱 | 制限強度 |
|-----------|-----------|---------|
| Tool Hallucination | Affordances | Hard block |
| Scope Violation | Affordances | Hard block |
| Cascading Failure | Goal-directedness | Budget limit |
| Parameter Injection | Affordances | Hard block |
| Excessive Autonomy | Goal-directedness | Budget limit |
| Silent Data Corruption | Goal-directedness | Soft warning |

---

## 設計原則

1. **Intelligence は味方**: エージェントの推論能力を制限するのではなく、Affordances と Goal-directedness を制限することで安全性を確保する
2. **Defense in Depth**: 1つの柱に依存しない。Affordances 制限（deny rules）+ Goal-directedness 制限（completion-gate）の多層防御
3. **Fail-closed for Policy**: セキュリティに関わるコントロールは `fail_closed=True` で実装し、エラー時に操作を許可しない
4. **Observable**: すべてのコントロールは検出結果をログに記録し、後から分析可能にする
