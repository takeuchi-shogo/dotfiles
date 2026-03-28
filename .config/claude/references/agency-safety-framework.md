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

### 認知バイアスリスク

LLM レビューアーは人間と同様の認知バイアスを持つ。特に以下に注意:

| バイアス | 説明 | 軽減策 |
|---|---|---|
| **確認バイアス** | コミットメッセージや PR description の著者説明に引きずられ、初期判断を正当化する方向に分析が歪む (arXiv:2603.18740) | Blind-first review（diff のみで分析後にコンテキスト確認）、adversarial framing（「レビュー」→「脆弱性を見つけろ」） |
| **アンカリング** | 最初に見た情報に判断が固定される | 複数モデルに非対称コンテキストを与える（codex-reviewer: diff のみ、code-reviewer: diff + コンテキスト） |
| **追従バイアス（Sycophancy）** | ユーザーが期待する結果に合わせて出力を捏造する。計算ステップを飛ばし結論だけ合わせる、検証したと虚偽申告する、パラメータを調整して期待出力に一致させる (Schwartz "Vibe Physics", 2026-03) | Adversarial self-check（「この結果が間違っていると仮定して、どこが壊れるか」を自問させる）、`rules/common/derivation-honesty.md` の遵守、M/L 規模での独立したクロスモデル検証 |

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

#### Known Limitations

| 限界 | 説明 | 現状の緩和策 | 改善候補 |
|---|---|---|---|
| **コマンドネスト検出** | regex ベースの deny rules は `$(cmd)` や `` `cmd` `` 内のサブコマンドを検出しない | `/careful` モードでの全コマンド確認 + settings.json deny rules の組み合わせ | Python AST (shlex + 再帰展開) による Bash コマンド解析 hook |

> **Qoder のアプローチ**: OS別ASTパーサーで全サブコマンドを抽出し、3層リスクチェックを適用。
> **優先度**: Low — エージェントが意図的にネストで deny rules を回避する確率は極めて低い。
> 実際のリスクは限定的であり、現状の deny rules + /careful モードで十分に緩和されている。

### Goal-directedness 制限（暴走を防ぐ）

エージェントが目標を過度に追求し続けることを防ぐ。

| コントロール | 場所 | 制限内容 |
|---|---|---|
| completion-gate.py | `scripts/policy/` | テスト実行の強制 + MAX_RETRIES=2 で無限ループ防止 |
| resource-bounds.md | `references/` | Doom-loop 検出（20 fingerprints, 3 repeats）、Exploration Spiral（5 consecutive reads） |
| stagnation-detector.py | `scripts/policy/` | 同種エラー反復・連続失敗・過剰編集を検出し戦略切替を提案 |
| improve-policy Rule 18 | `references/improve-policy.md` | 連続 reject 上限（3回で停止 + エスカレーション） |
| improve-policy Rule 19 | `references/improve-policy.md` | 目的メトリクス後退検出（ベースライン下回りで停止） |
| improve-policy Rule 20 | `references/improve-policy.md` | 単一変更規律（1イテレーション1変更のみ） |
| Context Pressure Levels | `references/resource-bounds.md` | 80% Warning → 90% Critical → 95% Emergency |
| C-008: 並行実行制約 | `references/constraints-library.md` | 他エージェントのファイル変更禁止 |
| improve-policy Rule 21-23 | `references/improve-policy.md` | Specification gaming 検出（Proxy metric 乖離、自己参照改善禁止、メトリクス多様性） |
| **Error Amplification Guard** | `references/subagent-delegation-guide.md` | 独立並列エージェントのエラー増幅リスク管理（下記参照） |

#### マルチエージェント エラー増幅

> Google Research "Towards a Science of Scaling Agent Systems" (2025) の実証データに基づく。

独立並列（エージェント間通信なし）ではエラーが **17.2倍** に増幅される。
中央集権型オーケストレーション（親が統合）では **4.4倍** に抑制可能。

| 協調モデル | エラー増幅率 | 対応する dotfiles パターン |
|---|---|---|
| 独立並列（通信なし） | 17.2x | `claude -p` 並列で結果を統合しない場合 |
| 中央集権型 | 4.4x | `/review`（親が結果を統合）、Agent ツール Sync |
| シングルエージェント | 1.0x（ベースライン） | 直接実行 |

**軽減策**:
1. **結果統合を必須にする**: 並列サブエージェントの結果は親が必ず統合・矛盾チェックする
2. **逐次推論タスクは並列化しない**: -39〜70% の劣化リスク（Task Parallelizability Gate 参照）
3. **矛盾検出**: 複数エージェントの出力が矛盾する場合、ユーザーに判断を委ねる（合成フェーズで自動解決しない）

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

## Adversarial Framing の副作用

> arXiv:2603.01213 "Can AI Agents Agree?" の知見。

防御的プロンプティング（adversarial framing）はレビュー品質を向上させるが、
**過度な脅威言及はエージェントの liveness を悪化させる** ことが実証されている。

| 条件 | Valid Consensus Rate | 収束速度 |
|------|---------------------|---------|
| 脅威言及なし (None Exist) | 75.4% | 約半分 |
| 脅威言及あり (May Exist) | 59.1% | 約2倍 |

### 設計指針

- **security-reviewer**: adversarial framing は有効。脆弱性検出が本務であり、警戒は正しい動作
- **code-reviewer, edge-case-hunter 等の汎用レビューア**: 過度な adversarial framing を避ける。「バグを見つけろ」は OK、「攻撃者がいるかもしれない」は品質劣化のリスクがある
- **合成フェーズ**: 矛盾検出時に「Byzantine agent かもしれない」という推論を挟まない。単に矛盾を列挙してユーザーに委ねる

### 判断基準

adversarial framing を使うべきか迷った場合:

| エージェントの本務 | framing | 理由 |
|-------------------|---------|------|
| セキュリティ検出 | 使う | 脆弱性検出には警戒が有効 |
| コード品質レビュー | 使わない | 過剰な警戒が false positive を増やし liveness を下げる |
| 合成・統合 | 使わない | 中立的に矛盾を報告すべき |

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
| **Context Bridging Injection** | MCP応答・スキル定義で悪意あるタスクをユーザータスクに文脈接続 | mcp-response-inspector.py + security-reviewer 4d | mcp-response-inspector.py (Soft warning) |
| **Supply-chain Skill Poisoning** | ClawHub等から取得したスキルの SKILL.md に攻撃パターン埋め込み | skill-security-scan.py G2 拡張 | skill-security-scan.py (Hard block on CRITICAL) |

### 3本柱との対応

| 障害モード | 関連する柱 | 制限強度 |
|-----------|-----------|---------|
| Tool Hallucination | Affordances | Hard block |
| Scope Violation | Affordances | Hard block |
| Cascading Failure | Goal-directedness | Budget limit |
| Parameter Injection | Affordances | Hard block |
| Excessive Autonomy | Goal-directedness | Budget limit |
| Silent Data Corruption | Goal-directedness | Soft warning |
| Context Bridging Injection | Affordances | Soft warning |
| Supply-chain Skill Poisoning | Affordances | Hard block |

---

## 設計原則

1. **Intelligence は味方**: エージェントの推論能力を制限するのではなく、Affordances と Goal-directedness を制限することで安全性を確保する
2. **Defense in Depth**: 1つの柱に依存しない。Affordances 制限（deny rules）+ Goal-directedness 制限（completion-gate）の多層防御
3. **Fail-closed for Policy**: セキュリティに関わるコントロールは `fail_closed=True` で実装し、エラー時に操作を許可しない
4. **Observable**: すべてのコントロールは検出結果をログに記録し、後から分析可能にする
