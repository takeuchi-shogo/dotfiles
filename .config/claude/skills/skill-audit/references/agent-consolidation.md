# Agent Consolidation Scan

`/skill-audit` skill の Agent Consolidation Scan セクションを切り出した詳細実装。
SKILL.md からは要約のみ参照され、ここで完全な手順 + 判定基準を保持する。

エージェント数の肥大化を防ぎ、統合候補を検出する。`/skill-audit consolidation` で単独実行、
または通常の audit ワークフロー末尾で自動実行。

## 背景

モデル能力の向上に伴い、1 エージェントが複数専門をカバーできるようになる。30+ エージェントの管理オーバーヘッドを定期的に評価し、skill modes 化（1 エージェント+複数モード）への統合判断材料を提供する。

## 手順

1. **エージェント一覧収集** — `~/.claude/agents/*.md` の frontmatter から name, description, tools を全件抽出
2. **ドメイン重複検出** — description のキーワードが重複するエージェントペアを抽出（閾値: 3 語以上の共通キーワード）
3. **使用頻度推定** — `git log --oneline -100` でエージェント名の出現頻度を計測。直近 100 コミットで起動ゼロのエージェントをフラグ
4. **統合候補判定** — 以下のいずれかに該当するペアを統合候補として提示:
   - 同一 tools セットを持ち、ドメインが隣接
   - 片方の機能が他方の機能の部分集合
   - 両方とも使用頻度が低い（直近 100 コミットで各 5 回未満）
5. **Orthogonality Check (出力種別の直交性)** — description から各エージェントの**主な出力種別**を推定し (`review-report` / `observation-report` / `plan` / `spec` / `implementation-patch` / `research-summary` など)、以下をフラグする:
   - 同一出力種別のエージェントが **3 体以上**存在 → 役割の直交性が低い。主エージェント + skill mode 化を検討
   - ドメインが異なっても出力種別が同じペア → 統合判定の補助シグナルとして提示（ドメイン重複とは独立に評価）

> **Orthogonality の原則**: 「エージェントの役割空間は出力種別 × ドメインの 2 軸で張る。同じセルに複数エージェントが居ると Expert Collapse または Role Confusion を起こしやすい」(2025-2026 マルチエージェント粒度研究より)

## 出力テーブル

```markdown
## Agent Consolidation Scan

| # | Agent A | Agent B | 重複理由 | 推奨アクション |
|---|---------|---------|---------|---------------|
| 1 | code-reviewer | golang-reviewer | Go レビューが code-reviewer の skill mode で可能 | 統合検討 |
| 2 | silent-failure-hunter | — | 直近 100 コミットで起動 0 回 | 退役 or 統合検討 |
```

## 判定基準

| パターン | アクション |
|---------|-----------|
| ドメイン重複 + 同一 tools | 統合を強く推奨 |
| 使用頻度ゼロ（100 コミット） | 退役候補としてフラグ（即削除しない） |
| 部分集合関係 | 親エージェントの skill mode 化を提案 |
