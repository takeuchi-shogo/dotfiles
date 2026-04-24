---
status: completed
date: 2026-04-24
type: absorb-analysis
sources:
  - github.com/google/skills (Apache-2.0, 13 GCP skills)
  - "From Skills to Systems: 5 Multi-Agent Orchestration Patterns in ADK 2.0" by addyosmani & Saboo_Shubham_ (Google Cloud Next 26)
outcome: 部分採択 — google/skills 13 全採択 (本業 GCP 利用), ADK 2.0 patterns 全 Already
---

# google/skills + ADK 2.0 Multi-Agent Orchestration Patterns absorb 分析

## Phase 1: Extract

### Source 1: github.com/google/skills

- GCP/Google 製品向け Agent Skills 集 (13 skill)
- ライセンス: Apache-2.0、883★、`npx skills add google/skills` 配布想定 (実際は gh skill install or 手動)
- 13 skill: gemini-api, alloydb-basics, bigquery-basics, cloud-run-basics, cloud-sql-basics, firebase-basics, gke-basics, recipe-{onboarding,auth,networking-observability}, waf-{security,reliability,cost-optimization}
- 主張: GCP 業務での skill 標準化、Well-Architected Framework 体系化
- 上流の不整合: ディレクトリ `google-cloud-networking-observability` だが SKILL.md `name:` は `google-cloud-recipe-networking-observability`

### Source 2: ADK 2.0 5 Multi-Agent Orchestration Patterns

1. Hybrid Graph: deterministic + AI-driven node を同一 graph、edge condition で flow 強制
2. Coordinator-Specialist: God agent 回避、`CoordinatorAgent` + specialists、`TransferProtocol.CONTEXTUAL`
3. Skill Composition: `SkillToolset` で skill を first-class、progressive disclosure
4. Cross-Language Pipeline: Python/TS/Go/Java SDK + A2A protocol + Agent Card (`/.well-known/agent-card.json`)
5. Sandboxed Executor: `SecureWorkspace(allowed_commands, network, max_execution_time, resource_limits)`

## Phase 2: Gap Analysis

### Gap/Partial/N/A (initial)

| #   | 手法                  | 初期判定 | 修正後             | 根拠                                                |
| --- | --------------------- | -------- | ------------------ | --------------------------------------------------- |
| A1  | npx skills add 配布   | N/A      | N/A 維持           | skills-lock.json 別運用方針確定                     |
| A2  | GCP 系 13 skill 取り込み | N/A      | **採択**           | 本業 GCP 利用判明 (ユーザー言明 2026-04-24)         |
| A3  | Recipe 系             | N/A      | **採択 (A2 と統合)** | GCP 業務で onboarding/auth は基礎                   |
| A4  | WAF 3 種              | N/A      | **採択 (A2 と統合)** | architecture 議論 reference として有用              |

### Already 強化分析

| #   | Pattern                | 既存                                                                              | 強化判定 | 根拠                                                  |
| --- | ---------------------- | --------------------------------------------------------------------------------- | -------- | ----------------------------------------------------- |
| B1  | Hybrid Graph           | blueprint-pattern.md + completion-gate.py + /autonomous DAG                       | 強化不要 | 個人開発で compliance audit 不要                      |
| B2  | Coordinator-Specialist | triage-router + model-routing.md + 30+ specialists                                | 強化不要 | Claude Code framework が CONTEXTUAL transfer 実装    |
| B3  | Skill Composition      | skill-invocation-patterns.md + atomic skill 3 原則 + composition depth 計測       | 強化不要 | description-based triggering で同等                   |
| B4  | Cross-Language Pipeline | cmux-ecosystem + dispatch + multi-model routing                                  | 強化不要 | 個人 dotfiles で多組織連携不要                        |
| B5  | Sandboxed Executor     | protect-linter-config + tool-scope-enforcer + MCP sandbox + agent-browser         | 強化不要 | kernel isolation は責任範囲外                         |

## Phase 2.5: Refine

- Codex 批評: codex-rescue agent forward 制約で取得失敗 (background task `bth105x81` output 0B)
- Gemini 補完で得られた知見:
  - google/skills は Vertex AI/Cloud Run 統合前提、Google エコシステム依存性高
  - ADK 2.0 patterns は LangGraph/Swarm/CrewAI と業界収束中、固有差別化は限定的
  - 個人スケールで Coordinator-Specialist は token cost 2.5-4x、ROI 低い
  - Pruning-First と整合: schema 確認だけして実装は自前が ROI 最大
- Gemini ハルシネーション部分 (ADK 2.0 GA Q3 2026 等) は採用せず

## Phase 3: Triage 結果

ユーザー回答 (2026-04-24): 「Firebase 以外だけど Firebase も入れておきたいので全て」
→ google/skills 13 全採択
→ ADK 2.0 patterns は強化不要を維持

## Phase 4: 統合プラン (実行済)

### 配布方式: β (skills-lock.json 統合)

- gh CLI v2.88.1 で `gh skill install` (v2.90+ 必要) 不可
- フォールバック: 手動 git clone → コピー + skills-lock.json 手書き更新
- commit: 6f0b8771638112948f03601e54f4602dd3cb7cc7

### 実行ステップ

1. /tmp/google-skills-clone に git clone
2. 13 skill を /Users/takeuchishougo/dotfiles/.config/claude/skills/ にコピー
3. ディレクトリ名 google-cloud-networking-observability → google-cloud-recipe-networking-observability にリネーム (SKILL.md frontmatter `name:` と整合)
4. 各 skill の computedHash を計算 (find -print0 + sort -z + shasum^2)
5. 各 skill の tree_sha を git ls-tree で取得
6. skills-lock.json に 13 entries を jq で merge (provenance: source/ref/commit_sha/tree_sha/resolved_at)
7. task skills:verify で 13 entries 全 ok 確認

### 検証結果

- 32 → 45 skill (+13)
- 新規 13 全て hash match (ok)
- 既存 6 mismatch (ui-ux-pro-max, vercel-composition-patterns, web-design-guidelines 等) は drift で別問題、今回スコープ外

### 名前衝突確認

- 既存 `gemini` skill (Gemini CLI ラッパ) ↔ 新規 `gemini-api` (Vertex AI/Agent Platform 文脈)
- description で明確分離、衝突なし

## Phase 5: Handoff

- 同一セッションで実行完了
- MEMORY.md "skills.sh 外部スキル" 16→45 更新
- _index.md に 1 行追記

## 棄却リスト (採択しなかった手法)

ADK 2.0 5 patterns の "強化不要" 判定:

- Hybrid Graph: 既に blueprint-pattern.md で同等
- Coordinator-Specialist: triage-router agent + Claude Code framework で実装済
- Skill Composition: skill-invocation-patterns.md + skill-conflict-resolution.md で対応
- Cross-Language Pipeline: cmux-ecosystem + dispatch skill + Codex/Gemini ルーティングで実装済
- Sandboxed Executor: hook 防御層 + MCP sandbox で対応 (kernel isolation は責任範囲外)

## Lessons learned

1. 「業務文脈の前提条件」は ユーザーに直接聞くのが最速 (Phase 3 で「GCP 業務薄い」を初期推定したが、実際は本業利用)
2. gh CLI v2.90+ 要件で `gh skill install` 不可 → 手動 clone フォールバックが必要
3. zsh の chpwd hook が `cd` 時に `ls` を呼んで shell スクリプトの hash 計算を破壊 → bash subshell でラップ必須
4. upstream のディレクトリ名と SKILL.md frontmatter `name:` が不整合な場合は `name:` 優先でローカルディレクトリ名を統一
5. codex-rescue agent は forward once 制約で background task に投げて exit する → Phase 2.5 Codex 批評は別経路 (codex-companion 直接 or codex skill) を要検討

## 関連ファイル

- skills-lock.json (32 → 45)
- /Users/takeuchishougo/dotfiles/.config/claude/skills/{alloydb,bigquery,cloud-run,cloud-sql,firebase,gemini-api,gke,google-cloud-recipe-*,google-cloud-waf-*}/
- 上流: github.com/google/skills @ 6f0b8771638112948f03601e54f4602dd3cb7cc7
