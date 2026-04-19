---
name: dependency-auditor
description: >
  package.json / go.mod / Cargo.toml / requirements.txt から脆弱性・放棄パッケージ・
  license 問題・major version lag を検査し、優先度付き修正リストを生成する。
  Triggers: '依存監査', 'dependency audit', 'npm audit', '脆弱性チェック', '放棄パッケージ',
  'outdated packages', 'license check', 'supply chain'.
  Do NOT use for: 新規依存の選定（選定基準は別途調査）、コード品質レビュー（use /review）、
  単発の npm install（直接コマンド実行）。
origin: self
allowed-tools: "Read, Write, Bash, Glob, Grep, Agent"
metadata:
  pattern: scanner+prioritizer
  version: 1.0.0
  category: security
---

# Dependency Auditor — 依存監査と優先度付け

プロジェクトの依存マニフェストを検出し、脆弱性・放棄・license・major version lag を
**独立した lens** で検査する。code-reviewer とは視点が異なり、
supply chain 視点に特化する。

## Philosophy

- **検出は自動、判断は人**: scan は並列実行で網羅するが、修正優先度は severity-matrix に基づく提案に留める
- **全部 update するな**: major version 一括 update は breaking change リスクが高い。段階的が原則
- **Silent な放棄が最も危険**: CVE より deprecated/unmaintained の方が長期リスクが大きい

## Workflow

### Phase 1: Detect

以下のファイルを repo root から Glob で検出:

| マネージャー | 検出ファイル | 前提ツール |
|------------|------------|-----------|
| **npm** | `package.json` + `package-lock.json` または `pnpm-lock.yaml` | `npm` / `pnpm` |
| **Go** | `go.mod` + `go.sum` | `go`, `govulncheck` (optional) |
| **Cargo** | `Cargo.toml` + `Cargo.lock` | `cargo`, `cargo-audit`, `cargo-outdated` (optional) |
| **Python** | `requirements.txt` / `pyproject.toml` / `Pipfile` | `pip`, `pip-audit` (optional) |

検出 0 件の場合: 「依存マニフェストが見つかりませんでした」と報告して早期 return。

### Phase 2: Scan (Sonnet に並列委譲)

検出されたマネージャーごとに並列で実行:

**npm/pnpm:**
```bash
npm audit --json           # 脆弱性
npm outdated --json         # major lag
```

**Go:**
```bash
go list -m -u all           # outdated
govulncheck ./...           # vuln (インストール済みなら)
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

`references/severity-matrix.md` に基づき、各 finding を以下に分類:

- **Critical**: CVSS ≥ 9.0 または RCE/Auth bypass、直接依存
- **High**: CVSS 7.0-8.9、deprecated かつ広く使用中
- **Medium**: CVSS 4.0-6.9、major lag 2+ versions、unmaintained > 2 年
- **Low**: CVSS < 4.0、minor/patch lag のみ、dev-dependency

### Phase 5: Report

優先度別にまとめた Markdown レポートを生成:

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

## High / Medium / Low
...

## Next Actions (優先度順)
1. {action 1}
2. {action 2}
```

**保存** (optional): ユーザー確認後 `docs/audits/deps-{YYYY-MM-DD}.md` に書き込む。

## Severity Matrix

詳細基準は `references/severity-matrix.md` を参照。

## Anti-Patterns

| # | ❌ Don't | ✅ Do Instead |
|---|---------|--------------|
| 1 | 全依存を一括 `npm update` | 優先度順に個別 update、PR 分割 |
| 2 | CI なしで lockfile だけ更新 | test/build が通ることを必ず検証 |
| 3 | Low を無視して Critical のみ対応 | Low も deferred list に記録 (累積 tech debt) |
| 4 | dev-dependency を本番と同列視 | dev は優先度を 1 段下げる (別分類) |
| 5 | `--force` で依存解決を強行 | peer dep 競合は upstream を確認 |

## Edge Cases

- **monorepo**: ルート + workspace 各 package の union を取る
- **lockfile なし**: 脆弱性スキャンは不能。「lockfile を生成してください」と指示
- **private registry**: `.npmrc` / `.netrc` の認証情報は読まない (セキュリティ)
- **proxy 経由**: scan 失敗時はネットワーク確認を促す

## Skill Assets

- `references/severity-matrix.md` — Critical/High/Medium/Low の判定基準 (CVSS based)

## Related Workflows

- コード品質レビュー → `/review` (code-reviewer / security-reviewer)
- AgentShield によるエージェント設定監査 → `/security-scan`
- commit 時の自動 lint → Lefthook (既設)
