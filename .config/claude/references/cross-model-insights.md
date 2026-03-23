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

---

## Archive

60日以上経過したエントリをここに移動する。

<!-- 現時点ではアーカイブ対象なし -->
