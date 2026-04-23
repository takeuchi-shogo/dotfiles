# Team Harness Patterns — 個人 → team 翻訳マップ

個人 dotfiles harness の仕組みを team project に持ち込むときの「何を / どう」翻訳するかの知識ベース。

## Why this doc

個人 harness (`scripts/policy/*.py`, `.config/claude/hooks/`, `settings.json`) を team repo にそのままコピーすると以下の問題が起きる:

- **権限**: 他メンバーの home にファイルを書けない
- **可搬性**: Python 3.14 前提 hook が team の CI (Python 3.12) で落ちる
- **維持**: bus factor 1、作った人が抜けると誰も触れなくなる
- **哲学衝突**: team では人間の合意・review が一次ゲート、hook は補助

→ 個人 harness の**仕組み**を、team に適した**別の機構** (GitHub native / CI / doc) に翻訳する。

## 翻訳マップ

| 個人 harness (dotfiles) | team 翻訳 | 理由 |
|------------------------|----------|------|
| `scripts/policy/completion-gate.py` (Stop hook で verify 強制) | PR template の check list + `.github/workflows/required-checks.yml` + Branch protection | team は人間 review が一次。hook は補助 |
| `.config/claude/hooks/protect-linter-config` | `.github/CODEOWNERS` で lint config ファイルに Senior reviewer 必須 | hook より CODEOWNERS が永続的 |
| `.config/claude/agents/codex-reviewer.md` (コード変更後の並列 review) | GitHub Actions で `codex-cli` 呼び出し (on: pull_request) + PR comment | CI で自動化、結果を PR に投稿 |
| `PLANS.md` (個人 plan ディレクトリ) | `docs/plans/` + Issue テンプレ | team は Issue を起点に plan を書く |
| `MEMORY.md` (個人 memory) | `docs/facts.md` + `docs/decisions/` (ADR) | team の集合知は immutable facts + 決定ログに分離 |
| `references/model-routing.md` (個人モデル使い分け) | `CLAUDE.md` の §10 (Agent Orchestration) + team 規約 | team は個人モデル設定に干渉しない |
| `scripts/learner/session-learner.py` (自動 retrospective) | PR merge 時の `.github/workflows/retro-digest.yml` (optional) | team 規模では Running Brief より Weekly Retro Meeting |
| `AutoEvolve` ループ | 四半期 retrospective + ADR の見直し | 自動化より人間の議論 |
| `.config/claude/rules/common/code-quality.md` | `.editorconfig` + `biome.json` + `.github/PULL_REQUEST_TEMPLATE.md` | static checker が強制、rules は補足 |
| `rules/common/security.md` | `docs/security/auth-payment-policy.md` + Branch protection | policy docs に codify |
| `.gitignore` + `pre-commit-check.js` (secret 検出) | team repo の `.gitignore` + GitHub Secret Scanning + gitleaks in CI | GitHub native で enforce |
| `docs/plans/active/` Ralph Loop | Issue + PR workflow | team は Issue ベース |
| `scripts/policy/completion-gate.py` の "proof required" | PR template の "Evidence" section (required) | 人間 review で enforce |

## What NOT to port

| 個人 harness 要素 | 持ち込み禁止理由 |
|-----------------|----------------|
| 個人 `settings.json` permissions.allow / deny | ユーザーごとに異なる。個人 settings は各自 |
| `scripts/policy/*.py` hook | Python 依存 & 書き込み権限 & 哲学衝突 |
| 個人 agent 定義 (`.config/claude/agents/`) | team では使うモデルが人により異なる |
| `docs/plans/active/` の plans ディレクトリ構造 | team は Issue/PR flow の方が自然 |
| AutoEvolve (session-learner / failure-clusterer) | 個人の学習サイクル、team では retrospective meeting |

## Core Parallels (持ち込む価値ある概念)

| 概念 | 個人 harness | team 翻訳 |
|------|-------------|----------|
| **Verification gate** | completion-gate.py で test pass 強制 | Required GitHub Checks + 2 approval |
| **Ownership-as-code** | (未実装) | `.github/CODEOWNERS` + OWNERSHIP.md |
| **Decision capture** | ADR (docs/adr/) | 同じ (ADR は team でも同構造) |
| **Scope caps** | `rules/common/code-quality.md` (800 行/ファイル) | CLAUDE.md §5 + PR template の "Lines changed" check |
| **Immutable fact index** | `references/*.md` | `docs/facts.md` (team で共有) |
| **High-risk area** (auth/payment) | `rules/security.md` + code-reviewer agent | 2-sign-off CODEOWNERS + branch protection + security workflow |

## Cross-model routing in team context

個人 harness は Claude / Codex / Gemini / Cursor を使い分けているが、team では:

- **team の CI**: Claude Code (claude-md-management plugin, claude-api skill 等) を GitHub Actions で起動
- **code review**: CI で Codex CLI を追加で回して差分 PR コメント投稿 (optional)
- **個人開発中**: 各自が dotfiles の個人 routing を使う (team の共通設定には含めない)

team repo の `CLAUDE.md` には「Primary/Subagent/Cross-Model の使い分けは dotfiles 側 references を参照」と一行ポインタだけ置き、詳細は個人側に委ねる。

## Typical team "harness minimum"

team project で最低限整備すべきもの (本 template が提供):

1. `CLAUDE.md` — project foundation (§1-12)
2. `docs/facts.md` — 不変事実の index
3. `docs/zones/OWNERSHIP.md` — Zone 所有権
4. `docs/decisions/` + ADR template — 意思決定ログ
5. `docs/security/auth-payment-policy.md` — 高リスク変更 policy
6. `.github/CODEOWNERS` — Zone ownership の機構化

これより厚い harness (CI workflow / secret scanning / 自動 retrospective) は project の成熟度 + team 規模に応じて段階的に追加する (YAGNI)。

## Adoption Path

新規 project に導入する順序 (痛点が大きい順):

1. **CLAUDE.md**: AI 使用時の foundation。無いと毎回前提を再説明
2. **CODEOWNERS**: PR review の自動アサイン。small team でも bus factor 対策
3. **facts.md**: 環境変数 / API URL の index。新メンバーの onboarding コスト激減
4. **ADR**: 決定が議事録に埋もれない。3 ヶ月後に「なぜ？」が復元できる
5. **OWNERSHIP.md**: CODEOWNERS の人間可読版。人事変更を反映
6. **auth-payment-policy**: 金銭 / 個人情報を扱い始めたとき

## Related

- Template 実体: `<dotfiles>/templates/team-project/{base,variants/}`
- 適用手順: `<dotfiles>/templates/team-project/APPLY.md`
- 関連 skill: `/init-project --team` (`<dotfiles>/.config/claude/skills/init-project/`)
- 設計根拠: `<dotfiles>/docs/plans/completed/2026-04-23-team-harness-template-plan.md`
- 起点 research: `<dotfiles>/docs/research/2026-04-23-team-harness-template-analysis.md` (後日生成)

## Review Cadence

- 新 team project で適用するたびに「どの translation が機能した / しなかった」を本ドキュメントに追記
- 四半期に 1 回 dead weight をレビュー (使われていない翻訳は削除)
