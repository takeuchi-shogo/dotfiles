---
name: dependency-auditor
description: >
  package.json / go.mod / Cargo.toml / requirements.txt から脆弱性・放棄パッケージ・
  license 問題・major version lag を検査し、優先度付き修正リストを生成する。
  Codex 用 read-only バージョン (Claude 版から Agent / Write 削除)。
  Triggers: '依存監査', 'dependency audit', 'npm audit', '脆弱性チェック', '放棄パッケージ',
  'outdated packages', 'license check', 'supply chain'.
  Do NOT use for: 新規依存の選定、コード品質レビュー (use `reviewer` agent)、単発の npm install。
origin: self
metadata:
  pattern: scanner+prioritizer
  version: 1.0.0-codex
  category: security
  platform: codex
---

# Dependency Auditor (Codex 版) — 依存監査と優先度付け

プロジェクトの依存マニフェストを検出し、脆弱性・放棄・license・major version lag を
**独立した lens** で検査する。`reviewer` agent とは視点が異なり、supply chain 視点に特化する。

**Codex 版の差分** (Claude 版との違い):
- Read-only mode のみ。レポートはターミナル出力。ユーザーが必要なら手動で保存する
- Subagent 委譲は Codex `[agents]` 経由で必要時のみ。デフォルトは shell 直接実行
- `references/severity-matrix.md` を同梱

## Philosophy

- **検出は自動、判断は人**: scan は並列実行で網羅するが、修正優先度は severity-matrix に基づく提案に留める
- **全部 update するな**: major version 一括 update は breaking change リスクが高い。段階的が原則
- **Silent な放棄が最も危険**: CVE より deprecated/unmaintained の方が長期リスクが大きい

## Workflow

### Phase 1: Detect

以下のファイルを repo root から検出 (`rg --files` で確認):

| マネージャー | 検出ファイル | 前提ツール |
|------------|------------|-----------|
| **npm** | `package.json` + `package-lock.json` または `pnpm-lock.yaml` | `npm` / `pnpm` |
| **Go** | `go.mod` + `go.sum` | `go`, `govulncheck` (optional) |
| **Cargo** | `Cargo.toml` + `Cargo.lock` | `cargo`, `cargo-audit`, `cargo-outdated` (optional) |
| **Python** | `requirements.txt` / `pyproject.toml` / `Pipfile` | `pip`, `pip-audit` (optional) |

検出 0 件の場合: 「依存マニフェストが見つかりませんでした」と報告して早期 return。

### Phase 2: Scan (shell 実行)

検出されたマネージャーごとに shell コマンドを順に実行 (Codex の `unified_exec` で並列化可):

**npm/pnpm:**
```bash
npm audit --json
npm outdated --json
```

**Go:**
```bash
go list -m -u all
govulncheck ./...
```

**Rust:**
```bash
cargo outdated --format json
cargo audit --json
```

**Python:**
```bash
pip list --outdated --format=json
pip-audit --format json
```

ツール未インストール時はスキップし、警告を結果に含める。

### Phase 3: Cross-reference

各パッケージの追加シグナルを確認:

- **deprecated**: npm `deprecated` field, Go module proxy, PyPI classifier
- **unmaintained**: GitHub 最終コミット > 2 年、repo archived
- **license**: SPDX identifier を抽出。`GPL-*` や unknown を警告
- **transitive depth**: 直接依存 or 間接依存

シグナル取得は best-effort。取れない場合は `unknown` として進める。

### Phase 4: Prioritize

`references/severity-matrix.md` に基づき、各 finding を分類:

- **Critical**: CVSS ≥ 9.0 または RCE/Auth bypass、直接依存
- **High**: CVSS 7.0-8.9、deprecated かつ広く使用中
- **Medium**: CVSS 4.0-6.9、major lag 2+ versions、unmaintained > 2 年
- **Low**: CVSS < 4.0、minor/patch lag のみ、dev-dependency

### Phase 5: Report

優先度別の Markdown レポートを **stdout に出力** する (Codex 版は Write しない):

```markdown
# Dependency Audit — {YYYY-MM-DD}

## Summary
- Scanned: {managers}
- Findings: Critical {c} / High {h} / Medium {m} / Low {l}

## Critical
### {package}@{version} — {CVE-ID}
- 問題: {description}
- 修正: `{manager} update {package}@{fixed-version}`
- 影響: direct / transitive via {parent}
- 検証: {test command or manual check}
```

ユーザーが保存を希望する場合のみ、`apply_patch` で `docs/audits/deps-{YYYY-MM-DD}.md` に書く (sandbox で許可されている時のみ)。

## Anti-Patterns

| # | ❌ Don't | ✅ Do Instead |
|---|---------|--------------|
| 1 | 全依存を一括 `npm update` | 優先度順に個別 update、PR 分割 |
| 2 | CI なしで lockfile だけ更新 | test/build が通ることを必ず検証 |
| 3 | Low を無視して Critical のみ対応 | Low も deferred list に記録 |
| 4 | dev-dependency を本番と同列視 | dev は優先度を 1 段下げる |
| 5 | `--force` で依存解決を強行 | peer dep 競合は upstream を確認 |

## Edge Cases

- **monorepo**: ルート + workspace 各 package の union を取る
- **lockfile なし**: 脆弱性スキャンは不能。「lockfile を生成してください」と指示
- **private registry**: `.npmrc` / `.netrc` の認証情報は読まない
- **proxy 経由**: scan 失敗時はネットワーク確認を促す

## Skill Assets

- `references/severity-matrix.md` — Critical/High/Medium/Low の判定基準

## Related (Codex)

- コード品質レビュー → `reviewer` agent
- セキュリティ深掘り → `security_auditor` agent
