# Build Agents that never forget — 分析レポート

- **日付**: 2026-04-14
- **著者**: Akshay Pachaar (@akshay_pachaar)
- **ソース**: ブログ記事（URL 不明、テキスト貼り付け経由）
- **フレームワーク**: LLM のステートレス問題を vector + graph + relational 3層ハイブリッドストアで解決する Cognee の設計思想

---

## 記事の主張（Thesis）

LLM はステートレスであり、セッションを跨ぐと文脈を忘れる。現状の主流な対策である Markdown ファイルベースのメモリ（CLAUDE.md / MEMORY.md など）は小規模では機能するが、ナレッジが増えると2つの壁にぶつかる:

1. **キーワード検索の壁** — 意味的に近くても文字列が一致しないと検索できない
2. **マルチホップ推論の壁** — 「Alice のプロジェクトは Tuesday の障害に影響されたか？」のような複数ステップの推論が直接検索では届かない

解決策として、認知科学のメモリ階層モデルを参考にした 3層ハイブリッドストア（Relational / Vector / Graph）を提案。Cognee はこれを `add` / `cognify` / `memify` / `search` の4つの async call で実装する。

---

## 抽出された手法（9 techniques）

| # | 手法 | キーワード | 根拠 |
|---|------|-----------|------|
| T1 | 認知科学的メモリ階層（Sensory / Working / Long-term → Episodic / Semantic / Procedural） | memory taxonomy | Miller 1956 (7±2)、認知科学の定説 |
| T2 | メモリ統合 consolidation: 反復事例を一般知識に昇華 | memory consolidation | 反復パターンから汎化ルールを抽出 |
| T3 | 3層ストア（Relational=provenance, Vector=semantics, Graph=relationships） | vector graph hybrid | 各ストアの長所を組み合わせてカバレッジ補完 |
| T4 | Entity dedup + dual indexing（graph node ⇔ embedding 双方向） | entity dedup | 重複エンティティによる検索精度劣化を防止 |
| T5 | Memify: 使用ログによる edge 重み自動調整 + stale node pruning | self-improving memory | 使用頻度に応じた重みで関連度を動的更新 |
| T6 | Session memory による代名詞解決 | session pronoun resolution | 「彼が言った」の「彼」を正しく解決 |
| T7 | Graph レベルの multi-tenant permission | multi-tenant memory | ユーザー/プロジェクト境界を graph のアクセス制御で実現 |
| T8 | Lost-in-middle 効果（長 context で中央情報 30% 精度低下） | context prioritization | Lost-in-middle 論文（Liu et al.）の実証データ |
| T9 | Multihop query: 複数エンティティ間の推論パスを graph traversal で解決 | multihop reasoning | 具体事例: Alice プロジェクト × outage 影響 |

---

## ギャップ分析結果（Codex + Gemini セカンドオピニオン反映済み）

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 | 強化方針 |
|---|------|------|------|---------|
| T3 | Vector / Graph DB 導入 | **N/A** | 7層アーキテクチャ設計はあるが個人 dotfiles への導入は未実施 | Codex・Gemini 合意: 固定運用コストが改善幅を上回る可能性が高い。導入しない |
| T4 | Entity extraction + dual indexing | **Partial** | fingerprint dedup のみ（`memory-safety-policy.md` 相当） | 軽量 entity index（JSONL）で追加可能。大規模 graph DB 不要 |
| T6 | Session 代名詞解決 | **Partial** | Session Memory 層 L3 は存在するが代名詞解決ロジックは未実装 | セッション内コンテキストを辿るシンプルな解決パスを追加 |
| T9 | Multihop traversal engine | **Partial** | MEMORY.md リンク + Agent tool で手動 multihop は可能。自動候補 path 生成・rank は未実装 | 2-hop 関連 memory 提示（クエリから隣接ノードを展開して提示）で実用的に対応 |

### Already 項目（既存実装の弱点と強化案）

| # | 既存の仕組み | 記事が示す弱点 | 強化案 | 優先度 |
|---|---|---|---|---|
| T1 | `memory-safety-policy.md` で Working / Procedural / Episodic / Semantic 4分類マッピング済み | — | 強化不要 | — |
| T2 | `session-learner.py` で outcome 分類 + パターン抽出 | implicit relationships（暗黙的関係性）の抽出 pass なし | consolidation 時に既存 fact 間の暗黙的関係性を LLM に抽出させる pass を追加 | 中 |
| T5 | `temporal-decay-policy.md` + `memory-eviction.py` で時間ベース decay | usage-based edge weight 未実装 | **最優先**: `friction-events.jsonl` や AutoEvolve 利用統計を feed し、usage-based boost を追加 | **高** |
| T7 | user / project / local 3スコープ + agent partition | 境界条件（権限・衝突・重複統合ポリシー）が明文化されていない | 境界条件とポリシーを docs に整理 | 低 |
| T8 | 7 Principles + PreCompact hook | 検索時の chunk selection / ordering / compression の担保が不明確 | 検証と documentation | 低 |

---

## セカンドオピニオン（Codex + Gemini）

### Codex の主な指摘

- **T3 を Partial → N/A に格下げ**: graph DB の固定費（スキーマ管理・embedding 再計算・schema drift 対応）は個人 dotfiles での改善幅を上回る可能性が高い。「設計済み」と「運用中」は別。
- **T9 の線引きを明確化**: 「人間 / agent が手動で辿れる」と「クエリから候補 path を自動生成・ランク付け」は別実装。後者が真の multihop traversal engine であり、現状は前者のみ。
- **T5 を最優先に**: time-based decay より usage-based boost の方が LLM エージェントの実際の記憶モデルに近く、既存 telemetry（friction-events.jsonl）と連携可能。

### Gemini の補完

- Markdown-only メモリの限界は実在（複数論文・OSS リポジトリで確認済み）。記事の問題提起は妥当。
- 2025-2026 の現実的代替: Anthropic Context Caching、Claude native memory、MCP server セマンティック検索。
- Cognify pipeline の隠れコスト: LLM 呼び出し増加、embedding 再計算、PII の graph 推論によるプライバシーリスク。
- 個人 dotfiles の最適解: **Markdown KB + MCP semantic search + git hook 索引 + Claude native memory** の組み合わせ。

---

## Phase 3 Triage — 取り込み決定

ユーザーが全項目の取り込みを選択。7項目すべてを統合プランに反映。

### 取り込むタスク

| ID | 内容 | 優先度 |
|----|------|--------|
| **A** | T5: usage-based edge weight（friction-events.jsonl と AutoEvolve 統計を活用） | 最優先 |
| **B** | T4: 軽量 entity index（JSONL ベース、重複抽出ロジック追加） | 高 |
| **C** | T9: 2-hop related memory 提示（自動候補 path 展開） | 高 |
| **D** | T2: implicit relationships 抽出 pass（consolidation 時に暗黙的関係を LLM 抽出） | 中 |
| **E** | T6: session 代名詞解決（セッション内コンテキスト辿り） | 中 |
| **F** | T7: 境界条件整理（権限・衝突・重複統合ポリシーを docs 化） | 低 |
| **G** | T8: compression 担保確認（PreCompact hook の chunk ordering 検証・docs 化） | 低 |

### 取り込まないもの

| 手法 | 理由 |
|------|------|
| T3: Vector / Graph DB | Codex・Gemini 合意で N/A。個人 dotfiles には運用コストが過剰 |
| T1: 4分類メモリ階層 | Already（強化不要）。既存実装で十分カバー |

---

## 実装プランへのリンク

実装詳細（タスク分解・実装ファイル・優先度ロードマップ）は以下を参照:

`docs/plans/2026-04-14-agent-memory-enhancement-plan.md`
