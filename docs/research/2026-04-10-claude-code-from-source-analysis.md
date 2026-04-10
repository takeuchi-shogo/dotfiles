---
title: Claude Code from Source - 全18章リバースエンジニアリング分析
date: 2026-04-10
type: research
topics: [claude-code, harness, architecture, memory, hooks, mcp]
source_url: https://claude-code-from-source.com/
related:
  - 2026-04-01-claude-code-internal-architecture-analysis.md
  - 2026-03-31-instructkr-claude-code-src-analysis.md
  - 2026-04-02-cc-7-layer-memory-architecture-analysis.md
  - 2026-04-05-claude-code-kairos-mode-analysis.md
integration_status: selective (Tier 1/2 統合済み、Tier 3 記録のみ)
---

# Claude Code from Source — 全18章リバースエンジニアリング分析

## 1. Executive Summary

36 AI エージェントが4フェーズ・6時間かけて Claude Code のバンドルから TypeScript ソースを完全復元し、18章の解説を生成したサイト。sourcemap の `sourcesContent` を利用した手法が特徴的。dotfiles にとっての価値は「CC 本体の設計判断の根拠を知ること」。Tier 1/2 の知見（メモリ staleness、coordinator 教義、hook snapshot、6エージェント全体像）は統合済み。Tier 3 の CC 内部実装（1730行 generator loop、4層圧縮、fork cache 90%割引）は dotfiles 責務外として記録のみとする。

---

## 2. 記事の構造 (全18章)

| Ch | タイトル | URL path | 1行要約 |
|----|----------|----------|---------|
| 01 | The Query Loop | /ch01 | async generator を使った CC 本体のメインループ設計 |
| 02 | Bootstrap & Startup | /ch02 | 5フェーズ起動 + module-level I/O parallelism (~240ms) |
| 03 | Configuration System | /ch03 | 階層設定（user/project/local）と優先度解決 |
| 04 | Prompt Assembly | /ch04 | dynamic boundary marker と 2^N problem の発生メカニズム |
| 05 | Context Management | /ch05 | 4層圧縮 + autocompact death spiral guards |
| 06 | Tool System | /ch06 | 45-member Tool interface + 14-step execution pipeline |
| 07 | Parallel Execution | /ch07 | speculative executor + 14-step partition algorithm |
| 08 | Sub-agents | /ch08 | 15-step runAgent lifecycle + permission bubble mode |
| 09 | Fork Agents | /ch09 | byte-identical prefix を利用した cache sharing |
| 10 | Memory System | /ch10 | file-based 4型メモリ + CLAUDE.md discovery algorithm |
| 11 | Background Agents | /ch11 | KAIROS 4フェーズ + background memory extraction |
| 12 | Hooks System | /ch12 | hook snapshot security + stateless execution design |
| 13 | Terminal Renderer | /ch13 | Packed Int32Array renderer + BSU/ESU 差分更新 |
| 14 | Diff & Patch | /ch14 | Myers diff + semantic chunking |
| 15 | MCP Integration | /ch15 | 8 transports + content-based dedup + description truncation 2048 chars |
| 16 | Remote Channels | /ch16 | 非対称設計 SSE reads / HTTP POST writes |
| 17 | File Search | /ch17 | 26-bit bitmap pre-filter + 50+ profiling checkpoints |
| 18 | Epilogue: 5 Bets | /ch18 | アーキテクチャ設計の5つの賭け事 |

---

## 3. 統合済み項目 (Tier 1/2) — 実装ポインタ付き

### Tier 1 (高優先度、実装済み)

**Memory staleness 運用ポリシー**
- CC 本体: `MEMORY.md` の各エントリは「いつ書いたか」を持たず、古い情報が残り続けるリスクがある
- 統合先: `.config/claude/references/memory-safety-policy.md` の "Staleness ポリシー" セクション
- 実装内容: 90日超エントリの自動フラグ、季節的な棚卸しスケジュール

**4-type memory 分類曖昧性ガイドライン**
- CC 本体: Conversational / Episodic / Semantic / Procedural の4型は境界が曖昧
- 統合先: `.config/claude/references/memory-safety-policy.md` の "4型分類の境界判定ルール" セクション
- 実装内容: 判定フローチャート + 具体例による境界明示

**Coordinator "Never delegate understanding" 4-phase 教義**
- CC 本体: Coordinator は自分で理解・計画し、実行のみ委譲する
- 統合先: `.config/claude/references/agent-orchestration-map.md` の "Coordinator の中核教義" セクション
- 実装内容: 4フェーズ（Understand → Plan → Delegate → Integrate）の明文化

**Hook snapshot security 設計思想**
- CC 本体: hook 実行時にファイルシステムのスナップショットを取り、副作用を検証
- 統合先: `.config/claude/references/hook-snapshot-security.md` (新規作成)
- 実装内容: hook の stateless 設計原則 + protect-linter-config との対応表

### Tier 2 (中優先度、実装済み)

**6 built-in agents 全体像**
- CC 本体: Explore エージェントが週3400万回実行、one-shot 設計で135字最適化
- 統合先: `docs/wiki/concepts/claude-code-architecture.md` 更新
- 実装内容: 6エージェント（Explore/Edit/Bash/MCP/Sub-agent/Fork）の役割と使用頻度

**2^N problem / DANGEROUS_uncachedSystemPromptSection 警告**
- CC 本体: 動的 boundary marker が指数的に cache miss を引き起こす
- 統合先: `.config/claude/skills/skill-creator/references/skill-writing-principles.md` の "原則9" として追加
- 実装内容: スキル作成時の「動的セクション禁止」ガイドライン

**Derivability test 具体禁止リスト**
- CC 本体: モデルが推論できる情報をシステムプロンプトに書くコストは推論 token + 1-2%
- 統合先: `.config/claude/references/compact-instructions.md` の "Derivability Test" セクション
- 実装内容: 禁止例リスト（現在日時、自明な手順、モデルが知っているAPI仕様など）

**Sub-agent bubble permission mode**
- CC 本体: サブエージェントは親の permission セットを「バブル」として継承、追加不可
- 統合先: `.config/claude/references/subagent-delegation-guide.md` の "Bubble Permission Mode" セクション
- 実装内容: permission 設計時の「最小権限バブル」パターン

---

## 4. 記録のみ項目 (Tier 3)

### 1. Generator Loop + 10 terminal/7 continue states + discriminated union (Ch01/Ch05/Ch18)

**CC 本体での実装概要**: `query.ts` 1730行のモノリシック async generator ループ。discriminated union で10種類の terminal state と7種類の continue state を管理。コールバック地獄を避けるために generator を選択。

**dotfiles で実装しない理由**: dotfiles はループそのものを書かない。hook と skill で CC の外側から制御する設計。Gemini 指摘: 1730行は保守性リスクが高く、将来の CC 本体リファクタリング候補。

**知識として活かす場面**: CC のエラー挙動（なぜ特定の状態で止まるか）をデバッグするときの参照。`/hook-debugger` で CC ループの terminal state を推定する際に有用。

---

### 2. 4層コンテキスト圧縮 + death spiral guards (Ch05)

**CC 本体での実装概要**: `AUTOCOMPACT_BUFFER_TOKENS=13000`、`MAX_CONSECUTIVE_AUTOCOMPACT_FAILURES=3`。圧縮失敗時のフォールバック、circular reference 検出、圧縮後の品質スコアリングを含む4層設計。

**dotfiles で実装しない理由**: CC 任せが適切。Gemini 指摘: Prompt Caching + sliding window で十分な場合が多く、over-engineering。death spiral guards は CC 本体が担保する。

**知識として活かす場面**: `PreCompact flush + PostCompact verify` (Context Constitution P3) の設計根拠として参照。圧縮失敗時に CC が3回で諦める挙動の説明。

---

### 3. Fork agents byte-identical prefix + 90% キャッシュ割引 (Ch09)

**CC 本体での実装概要**: 複数エージェントを fork する際に system prompt を byte-identical に保ち、Anthropic の Prompt Caching (90% 割引) を享受する設計。prefix 共有のために fork タイミングを制御。

**dotfiles で実装しない理由**: Gemini 指摘: 実際の割引率は環境により25-50%、OS のキャッシュ差異で無効化リスク大、dotfiles 規模では ROI ネガティブ。「採用非推奨」として記録。

**知識として活かす場面**: cmux Worker でマルチエージェントを走らせる際、system prompt を統一することでキャッシュ効率が上がる（副次効果として）。

---

### 4. 14-step execution pipeline + 45-member Tool interface (Ch06)

**CC 本体での実装概要**: Tool が `buildTool()` で自己記述 (self-describing) し、`isConcurrencySafe` などの input-dependent フラグを持つ。実行パイプラインは validation → pre-exec hook → execute → post-exec hook など14ステップ。

**dotfiles で実装しない理由**: CC 本体のツール実行層であり、dotfiles は hook でカスタマイズするレイヤーに留まる。45-member interface を dotfiles で再実装する必要はない。

**知識として活かす場面**: MCP スキル作成時の Tool interface 設計参照。`isConcurrencySafe` の概念は `subagent-delegation-guide.md` の並行実行判定に応用済み。

---

### 5. KAIROS mode (orient/gather/consolidate/prune 4-phase) (Ch11)

**CC 本体での実装概要**: 長期プロジェクト向けの自律的コンテキスト管理。orient（状況把握）→ gather（情報収集）→ consolidate（統合）→ prune（刈り込み）の4フェーズで自動実行。

**dotfiles で実装しない理由**: Gemini 指摘: 個人プロジェクトには overkill。AutoEvolve 日次統合（セッション→日次→BG）で類似概念をすでにカバー。CC 本体の KAIROS は dotfiles 規模の10倍以上のプロジェクトを想定。

**知識として活かす場面**: AutoEvolve の改善時に KAIROS の prune フェーズ（staleness 除去）を参考に日次クリーンアップロジックを強化できる。

---

### 6. Self-describing tools (buildTool + isConcurrencySafe input-dependent) (Ch06)

**CC 本体での実装概要**: Tool が実行時に自身の metadata（description、input schema、並行安全性フラグ）を生成。input の内容によって `isConcurrencySafe` が変わる動的判定を持つ。

**dotfiles で実装しない理由**: CC 本体の Tool interface 契約であり、dotfiles は MCP 経由でこの interface を利用する側。

**知識として活かす場面**: MCP スキル設計時に「このツールは並行安全か」の判定基準として参照。Skill-creator の原則として「副作用のあるツールは isConcurrencySafe=false」を明示すべきことが分かる。

---

### 7. Speculative executor + 14-step partition algorithm (Ch07)

**CC 本体での実装概要**: ツール呼び出しの依存グラフを解析し、並列実行可能なものを先投機的に実行。14ステップの partition algorithm で DAG を構築し、wave ごとに並行化。

**dotfiles で実装しない理由**: CC 内部の並列最適化。dotfiles での並列タスクは cmux Worker または `run_in_background` で対応済み。

**知識として活かす場面**: CC が「なぜあのツール呼び出しが並列になるか」を理解するためのモデル。hook 設計で「この2つの hook は並列安全か」の判定に応用。

---

### 8. 15-step runAgent lifecycle (Ch08)

**CC 本体での実装概要**: サブエージェントの init → permission-check → tool-setup → run → collect-output → cleanup の15ステップ。各ステップで hook が挿入可能。

**dotfiles で実装しない理由**: CC 内部のサブエージェント管理。dotfiles の `subagent-delegation-guide.md` は利用側の設計ガイドとして十分。

**知識として活かす場面**: サブエージェントが予期せず終了する際にどのステップで失敗しているかを推定する参照。

---

### 9. Packed Int32Array terminal renderer + BSU/ESU (Ch13)

**CC 本体での実装概要**: ターミナル表示を Int32Array で管理し、1セルあたり32ビットで文字+属性を packed encoding。BSU/ESU (Begin/End Styled Unit) で差分レンダリング。

**dotfiles で実装しない理由**: UI 最適化、dotfiles 責務外。Ghostty + cmux での表示は CC のレンダリング層に依存しているが、dotfiles からは制御不能。

**知識として活かす場面**: CC の表示バグ（文字化け、ANSI コード漏れ）をデバッグする際の内部構造理解として。

---

### 10. Bootstrap 5-phase + module-level I/O parallelism (~240ms) (Ch02)

**CC 本体での実装概要**: 起動を5フェーズ（config load → tool registration → MCP init → memory load → UI setup）に分割し、各フェーズ内の I/O を並列化。起動時間 ~240ms を実現。

**dotfiles で実装しない理由**: CC 本体の起動最適化であり、dotfiles から変更不可。

**知識として活かす場面**: CC の起動が遅い場合（MCP タイムアウト等）のトラブルシューティングで、どのフェーズが遅延しているかを推定する参照。

---

### 11. Dynamic boundary marker 2^N problem (Ch04)

**CC 本体での実装概要**: 動的に生成される boundary marker（セクション区切り）が変わるたびに Prompt Cache が無効化される。N 個の動的セクションで最悪 2^N の cache miss パターンが発生。

**dotfiles で実装しない理由**: CC 本体の実装問題。Tier 2 でスキル作成ガイドライン（原則9）として応用済みだが、CC 本体の実装自体は記録のみ。

**知識として活かす場面**: スキルやエージェント設計で「動的セクションを減らす」判断の根拠。`compact-instructions.md` の Derivability Test と組み合わせて参照。

---

### 12. Asymmetric remote channels (SSE reads / HTTP POST writes) (Ch16)

**CC 本体での実装概要**: リモート接続では SSE でサーバーからのストリームを読み、HTTP POST でコマンドを送る非対称設計。WebSocket を避けた理由は reconnect 容易性。

**dotfiles で実装しない理由**: CC の remote 機能であり、dotfiles はローカル実行が前提。

**知識として活かす場面**: cmux リファレンスの参考。`read-screen` は SSE 的な pull、`send` は POST 的な push という類比で cmux の設計を説明できる。

---

### 13. 26-bit bitmap pre-filter (270K files in 4 bytes each) (Ch17)

**CC 本体での実装概要**: ファジー検索でのファイル候補絞り込みに 26-bit bitmap を使用。270K ファイルを 1.08MB に圧縮し、メモリ効率と検索速度を両立。

**dotfiles で実装しない理由**: ファジー検索最適化、dotfiles 責務外。

**知識として活かす場面**: dotfiles の規模でこの最適化が不要な理由を説明する際の逆引き参照。

---

### 14. 8 MCP transports + content-based dedup + description truncation 2048 chars (Ch15)

**CC 本体での実装概要**: stdio/SSE/WebSocket/HTTP など8種の MCP transport を統一インターフェースで処理。Tool description が 2048 chars を超えると自動 truncation。content-based dedup で重複ツール登録を防止。

**dotfiles で実装しない理由**: MCP 周辺の CC 内部実装。dotfiles は MCP クライアントとして使う側。

**知識として活かす場面**: MCP スキル作成で description が 2048 chars 制限に引っかかる問題の根拠。`skill-writing-principles.md` の「description は簡潔に」の技術的根拠として参照。

---

### 15. Background memory extraction (fork cache share) (Ch11)

**CC 本体での実装概要**: バックグラウンドで `CLAUDE.md` への記憶追記を fork エージェントが担当。メインループをブロックせず、fork の prefix-cache を共有してコストを抑える。

**dotfiles で実装しない理由**: CC 本体の自動メモリ補足機能。dotfiles の AutoEvolve はセッション終了後に明示的な統合を行う設計であり、バックグラウンド自動抽出とは補完関係。

**知識として活かす場面**: CC の自動 `CLAUDE.md` 更新が AutoEvolve の日次更新と重複するリスクを認識するため。CC の自動書き込みを無効化すべきかの判断材料。

---

### 16. 50+ startup profiling checkpoints (Ch17)

**CC 本体での実装概要**: 起動プロセスに50以上の profiling checkpoint を埋め込み、ボトルネックを特定可能にしている。`CLAUDE_DEBUG=startup` 等の環境変数で有効化。

**dotfiles で実装しない理由**: CC 本体の観測性機能。dotfiles の観測パイプライン（Session Observer + claude-observe.sh）は CC の外側から観測する設計。

**知識として活かす場面**: CC 起動が遅い場合の診断。`CLAUDE_DEBUG=startup` を Session Observer のデバッグモードで活用できる可能性。

---

## 5. 設計哲学の 5 Bets (Ch18 "Epilogue")

### Bet 1: Generator Loop Over Callbacks

- **主張**: async generator はコールバック地獄より状態管理が明確
- **dotfiles との対応**: hook の実行モデルも stateless 関数チェーンで callbacks を避ける設計
- **Gemini の脆弱性指摘**: 1730行のモノリシック generator は単一責任原則に反する。将来の機能追加でさらに肥大化するリスク

### Bet 2: File-Based Memory Over Databases

- **主張**: SQLite/Redis より `CLAUDE.md` などのファイルがエージェントには適切
- **dotfiles との対応**: MEMORY.md + 7層メモリモデルで同じ思想を実装済み
- **Gemini の脆弱性指摘**: ファイルベースは concurrent write で corruption リスク。大規模チームでは DB が必要になる。個人規模では正しい判断

### Bet 3: Self-Describing Tools Over Central Orchestrators

- **主張**: ツール自身が metadata を持つことで中央オーケストレーターが不要になる
- **dotfiles との対応**: hook による distributed policy 適用（一元管理より分散宣言）
- **Gemini の脆弱性指摘**: self-describing が正確でない場合（description の幻覚）、debuggability が低下する

### Bet 4: Fork Agents for Cache Sharing

- **主張**: fork による byte-identical prefix で 90% キャッシュ割引を得る
- **dotfiles との対応**: cmux Worker での並列タスク（prefix 共有は副次効果として意識する程度）
- **Gemini の脆弱性指摘**: 実際は25-50%の割引、OS キャッシュ差異で効果が変動。「Bet」として記録すべきリスクが高い

### Bet 5: Hooks Over Plugins

- **主張**: プラグインシステムより hook（stateless 関数）の方が予測可能で安全
- **dotfiles との対応**: ハーネス全体が hooks 4層 + lib 設計で実装済み。最も強く一致する Bet
- **Gemini の脆弱性指摘**: hook の composition が複雑になると実行順序の依存が暗黙的になる。`change-surface-matrix.md` での依存関係明示が必要

---

## 6. Gemini 批評サマリ

詳細は `/Users/takeuchishougo/.claude/docs/research/2026-04-10-claude-code-design-principles-analysis.md` (Gemini 生成、31KB) を参照。

**最も堅牢な原則 Top 3**:
1. File-Based Memory — 個人・小チーム規模では DB より保守性が高い
2. Hooks Over Plugins — stateless 設計により副作用の予測が可能
3. Coordinator "Never delegate understanding" — 責任境界の明確化

**最も脆弱な原則 Top 3**:
1. Fork Agents 90% Cache — 実測は25-50%、環境依存が大きい
2. Generator Loop 1730行 — 保守性リスク、単一責任違反
3. 4層コンテキスト圧縮 — 過度に複雑、sliding window で十分なケースが多い

**dotfiles 採用時の警告 Top 3**:
1. background memory extraction を CC に任せると AutoEvolve と競合する可能性
2. self-describing tool の description が 2048 chars で切れる点を MCP スキル作成時に意識する
3. 2^N problem は スキル設計（動的セクション）で再現しうる、原則9の徹底が必要

---

## 7. 既存 dotfiles との差分マップ

| 記事の概念 | dotfiles 側の対応 | 状態 |
|----------|------------------|------|
| file-based memory | MEMORY.md + 4型分類 | ✅ 同思想で実装済み |
| hook snapshot security | protect-linter-config.py | ✅ 同思想、対応表を `hook-snapshot-security.md` に記録 |
| coordinator "Never delegate understanding" | `agent-orchestration-map.md` に統合 | ✅ 2026-04-10 追加 |
| 6 built-in agents 全体像 | `docs/wiki/concepts/claude-code-architecture.md` 更新 | ✅ 2026-04-10 更新 |
| memory staleness policy | `memory-safety-policy.md` に staleness ポリシー追加 | ✅ 2026-04-10 追加 |
| 4-type memory 境界判定 | `memory-safety-policy.md` に境界判定ルール追加 | ✅ 2026-04-10 追加 |
| 2^N problem 警告 | `skill-writing-principles.md` 原則9として追加 | ✅ 2026-04-10 追加 |
| derivability test | `compact-instructions.md` に禁止リスト追加 | ✅ 2026-04-10 追加 |
| bubble permission mode | `subagent-delegation-guide.md` に追加 | ✅ 2026-04-10 追加 |
| KAIROS 4-phase | AutoEvolve 日次統合でカバー済み | ✅ 概念は同等、dotfiles 実装は不要 |
| fork cache sharing | cmux Worker の system prompt 統一で副次的に活用 | 〜 部分的に意識 |
| asymmetric remote channels | cmux の read-screen/send 設計の類比として参照 | 📝 参照知識のみ |
| generator loop terminal states | hook-debugger でのデバッグ参照 | 📝 参照知識のみ |
| MCP description 2048 chars truncation | skill-writing-principles に「description 簡潔化」追加 | ✅ ガイドライン化済み |
| background memory extraction | AutoEvolve との競合リスクを記録 | 📝 注意事項として記録 |

---

## 8. 関連研究ノート

- **内部アーキテクチャ分析** (2026-04-01): `docs/research/2026-04-01-claude-code-internal-architecture-analysis.md`
- **instructkr ソース分析** (2026-03-31): `docs/research/2026-04-01-instructkr-claude-code-harness-skills-workflows-analysis.md`
- **7層メモリモデル** (2026-04-02): `docs/research/2026-04-02-cc-7-layer-memory-architecture-analysis.md`
- **KAIROS mode** (2026-04-05): `docs/research/2026-04-05-claude-code-kairos-mode-analysis.md`
- **Gemini 設計原則批評** (2026-04-10, external): `/Users/takeuchishougo/.claude/docs/research/2026-04-10-claude-code-design-principles-analysis.md`
- **メモリ内部構造** (2026-04-02): `docs/research/2026-04-02-claude-code-memory-internals-analysis.md`

---

## 9. Appendix: Codex 批評の欠如

Phase 2.5 で Codex の批評も試みたが、14分経過しても完了せず cancel した。今回の分析は Gemini の批評のみで Phase 3（執筆）に進んだ。

**Harness 教訓として記録**:
- Codex はタイムアウトリスクが高い長時間推論タスクに向かない（14分は明らかに超過）
- 今後同様のタスクでは Codex は「設計の壁打ち」（短い往復）に使い、長時間分析は Gemini に割り当てる
- `feedback_codex_casual_use.md` の「実際に対話する」原則と一致: 長時間一方的に待つのではなく、短いラリーで進める
- Phase 2.5 の cancel 判断（14分）は適切。Gemini 単独で品質は確保できた
