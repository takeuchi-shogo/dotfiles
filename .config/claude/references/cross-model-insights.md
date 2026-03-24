# Cross-Model Insight Registry

HACRL (Heterogeneous Agent Collaborative RL) の双方向知識転移に基づき、各モデルが発見した reusable insight を蓄積する。
全エージェントが教師・生徒の両方の役割を担い、過去セッションの知見を次回の実装・レビュー・分析に活かす。

## 更新ポリシー

- `/analyze-tacit-knowledge` の Cross-Model Insight Export ステップから自動追記
- 手動追記も可（セッション中に有用な知見を発見した場合）
- 各エントリには `date`, `source_session`（任意）, `domain`, `insight` を記載
- 鮮度管理: 60日以上前のエントリは Archive セクションに移動

---

## Codex Insights

深い推論・リスク分析・障害モード特定から得られた知見。

| date | domain | insight |
|------|--------|---------|
| 2026-03-23 | hook-design | pre-commit hook で正規表現の `\b` を使うと日本語混在テキストで誤マッチする。`(?=[^a-zA-Z0-9]|$)` に置換すべき。Codex リスク分析で障害モードとして検出 |

## Gemini Insights

大規模コンテキスト分析・エコシステム調査・マルチモーダル処理から得られた知見。

| date | domain | insight |
|------|--------|---------|
| 2026-03-23 | architecture | dotfiles の symlink 構造で `~/.claude/references/` は直接 symlink されていないため、hook から参照する際は `lib/hook_utils.py` の `resolve_reference()` を経由する必要がある。Gemini の 1M コンテキスト分析でパス解決の不整合として発見 |

## Claude Insights

実装経験・デバッグ・パターン発見から得られた知見。

| date | domain | insight |
|------|--------|---------|
| 2026-03-23 | memory-system | MEMORY.md はセッション開始時の静的スナップショットであり、セッション中の更新は次セッションまで system prompt に反映されない。checkpoint/handoff 時は plan ファイルにも必要情報を書く必要がある |
| 2026-03-25 | context-management | **Context Anxiety のモデル別感受性差**: Sonnet 4.5 はコンテキスト 75-80% で早期打ち切り（premature wrapping）が顕著。Compaction だけでは解消せず full context reset が必要。Opus 4.6 では大幅に軽減されたが完全には消えない。長時間タスクでモデルを選択する際の判断材料。(出典: Anthropic "Harness Design for Long-Running Apps", 2026-03) |

---

## Shared Blind Spots

> 全モデルが一致する結果は信頼度が上がるが、**正しさの証明ではない**。
> LLM は共通の学習データ・アーキテクチャから類似のバイアスを共有するため、
> 全モデルが同じ間違いをするケースがある。
> (Schwartz "Vibe Physics", 2026-03: Claude/GPT/Gemini 全てが MS-bar subtraction と log(4π) 因子を見落とした)

### レビューアー数増加と盲点リスク

> Del et al. (arXiv:2603.19118): VC と SC の Kendall τ 相関はサンプル数増加で**単調増加**する。
> つまりレビューアーを増やすほど指摘が収束し、**全員が同じ方向を向く**。
> これは一見「合意の質が上がった」ように見えるが、実際には共有盲点の検出力は向上しない。

- N=2（異種）で得られる相補性が最も高く、N が増えるほど信号は収束する
- 「全レビューアーが PASS」は安心材料だが、**盲点が無いことの証明ではない**
- 盲点を検出するには、レビューアーを増やすより**異なるパラダイム**（手動テスト、ユーザーテスト、production monitoring）が有効

### 記録すべきケース

- 全モデルが一致した結論が後で誤りと判明したケース
- 特定のドメイン知識で全モデルが共通の誤解を示したケース

### 対策

- クロスモデル全一致でも「検証済み」ではなく「信頼度が高い」と表現する
- 重要な判断では、モデル出力だけでなく外部ソース（公式ドキュメント、テスト実行結果）で裏取りする
- 既知の盲点パターンをこのセクションに蓄積し、同種の判断時に参照する

| date | domain | blind_spot |
|------|--------|------------|
| — | — | (初期エントリなし。発見次第追記) |

---

## Archive

60日以上経過したエントリをここに移動する。

<!-- 現時点ではアーカイブ対象なし -->
