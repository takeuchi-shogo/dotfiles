---
source: "https://github.blog/changelog/2026-04-16-manage-agent-skills-with-github-cli/"
date: 2026-04-19
status: analyzed
---

## Source Summary

**主張**: GitHub CLI v2.90 で `gh skill` コマンド (install/search/update/publish) が追加。Agent Skills 仕様準拠で Claude Code/Cursor/Codex/Gemini 横断のスキル配布を統一化。commit SHA + タグベースのバージョンピニング、SKILL.md frontmatter に portable provenance (source repo, ref, Tree SHA)、タグ保護+コードスキャンでサプライチェーン整合性を担保。

**手法**:
- `gh skill install <repo> <name>[@version]` - 対話型検出 + インストール
- `gh skill install ... --pin <tag>` - イミュータブルなタグピニング
- `gh skill install ... --agent <platform>` - Claude Code/Cursor/Codex/Gemini 指定
- `gh skill search <keyword>` - キーワード検索
- `gh skill update [--all]` - アップストリーム同期・drift 検知
- `gh skill publish` - 仕様検証 + セキュリティチェック付き公開
- SKILL.md frontmatter の portable provenance (repo/ref/tree_sha)

**根拠**: Git タグ+コミット SHA による供給チェーン整合性。Post-publication 改ざん防止。セキュリティ推奨: タグ保護・コードスキャン有効化。

**前提条件**: GitHub CLI v2.90.0 以上。GitHub 依存 (private repo は GH_TOKEN 必須、エアギャップ環境不可、リージョン制限の可能性)。

## Gap Analysis (Pass 1: 存在チェック)

| # | 手法 | 判定 | 詳細 |
|---|------|------|------|
| 1 | `gh skill install` 統一 CLI | Partial | `init-install.sh::setup_claude_plugins()` で plugin install のみ。個別 skill は skills-lock.json ベース、統一 CLI なし |
| 2 | `gh skill update` / drift 検知 | Gap | skills-lock.json に hash 保存するが upstream 変更検知なし |
| 3 | Version pinning (commit SHA + tag) | Partial | `computedHash` のみ。commit SHA/タグ未記録 |
| 4 | `gh skill publish` / 公開ワークフロー | Low-priority (was Gap) | 個人 dotfiles、公開配布予定なし |
| 5 | `gh skill search` | N/A | ローカル 539 スキルにはファイルシステム検索で十分 |
| 6 | サプライチェーンセキュリティ | Partial (外部由来のみ) | 自作スキルは threat model 外 |

## Already Strengthening Analysis (Pass 2: 強化チェック)

| # | 既存の仕組み | 記事が示す弱点 | 強化案 | 判定 |
|---|---|---|---|---|
| A | SKILL.md frontmatter (name/description/allowed-tools) | portable provenance 欠落 | provenance (source/ref/tree_sha) 追記 | 強化可能 → 最優先格上げ |
| B | symlink.sh (.bin/symlink.sh) | 4 スキルのみ手動 symlink、追加時忘れやすい | frontmatter の `platforms:` 宣言から自動生成 | 強化可能 |
| C | skills-lock.json (computedHash のみ) | commit SHA/タグ未記録、監査時に不明瞭 | commit, tag, resolved_at 追加 | 強化可能 → 最優先格上げ |

## Phase 2.5 批評サマリ

**Codex (codex-rescue)**:
- #4/#6 過大評価: 個人運用なら Low-priority。threat model を外部取り込みスキルに絞る
- A (provenance) 過小評価: 「強化可能」ではなく最優先
- 539 スキル一括移行は危険。外部由来・高頻度更新・複数環境共有に絞る
- 見落とし: rollback、private/forked/local-only、互換性テスト
- 結論: Partial adopt。gh skill は wrapper/実験に留め、symlink 管理を急に置き換えない

**Gemini**:
- GitHub 依存・エアギャップ不可・private repo 認証必須
- AI 特有のサプライチェーンリスク (prompt injection 型スキル、資格情報抜き取り)
- MCP との並行標準化に注意

## Integration Decisions

### Gap / Partial

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| 1 | skills-lock.json provenance 追加 | 採用 (P1) | Codex が最優先と判定、監査可能性に直結 |
| 2 | 外部由来スキル drift 検知 | 採用 (P1) | upstream 変更の盲点解消 |
| 3 | SKILL.md origin: 分類 | 採用 (P2) | drift 検知と symlink 自動化の基盤 |
| 4 | symlink.sh platforms: 自動化 | 採用 (P2) | 追加忘れ防止 |
| 5 | rollback 機構 | 採用 (P3) | Codex 見落とし指摘から追加 |
| 6 | gh skill wrapper 実験 | 採用 (P3) | 採用判断は wait-and-see |
| 7 | 外部スキル hash 検証 | 採用 (P3) | install 時の整合性担保 |
| 8 | 公開ワークフロー | スキップ | 個人運用では不要 |
| 9 | タグ保護・署名 | スキップ | hash 検証で十分 |

## Plan

詳細は `docs/plans/2026-04-19-gh-skill-absorb-plan.md` を参照。7 タスク、L 規模。Wave 1 (T1-T3 Foundation) → Wave 2 (T4-T5 Runtime) → Wave 3 (T6-T7 Safety) の段階実行を推奨。
