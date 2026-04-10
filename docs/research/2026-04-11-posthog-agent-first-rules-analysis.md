---
source: "PostHog Blog — The golden rules of agent-first product engineering by Jina Yoon"
date: 2026-04-11
status: integrated
---

## Source Summary

**主張**: エージェント（LLM）がファーストクラスのユーザーとして製品を使う時代に向けて、5つの原則に従って設計・運用すべき。PostHog MCP の 6K+ DAU と2度のアーキテクチャ刷新に基づく実践知。

**手法**:
1. **API parity** — エージェントがユーザーと同じことを何でもできるようにする（OpenAPI → Zod → YAML opt-in → tool handler パイプライン）
2. **Raw primitive 露出** — `get-insight` 等 4 tool を `executeSql` 一本化。抽象ではなく Lego ブロック（原始部品）を渡す
3. **Front-load universal context** — v1 は 4 行 "GLHF"、v2 は taxonomy + SQL 構文 + 必須ルールに刷新
4. **Skills as onboarding, not manuals** — idiosyncratic knowledge / edge cases / taste & craft を書く。良いマネージャ比喩（プロセスより文脈）
5. **Treat agents like real users** — CLI dogfooding, weekly traces hour, 良い/悪い挙動を eval 化

**根拠**: PostHog MCP の実運用データ（6K+ DAU）、read endpoint 全廃（SQL 一本化）、traces hour による silent failure 発見。定量的なビフォーアフター比較あり。

**前提条件**: SaaS プロダクトが MCP/tool を外部 LLM エージェント向けに公開するケース。単一チームが自社 harness を使う場合は力点が異なる。

## Gap Analysis (Pass 1: 存在チェック)

| # | 手法 | 判定 | 詳細 |
|---|------|------|------|
| 1 | API parity（エージェントが何でもできる） | Already | delegation policy 明示（CLAUDE.md `agent_delegation` タグ）。ただし subagent tool ホワイトリストの境界が曖昧 |
| 2 | Raw primitive 露出（wrapper stack を薄くする） | Partial | cmux/codex/gemini CLI は raw 呼び出し。一方で convenience wrapper が積み上がっており、どこまで raw にすべきかの判断基準が未文書化 |
| 3 | Front-load universal context | Already | Progressive Disclosure（CLAUDE.md 130行 → references/ → rules/）+ 7層メモリ + `<important if>` 条件タグで充実 |
| 4 | Skills as onboarding（マニュアルではなく文脈） | Already | DBS rubric・Atomic Skills 原則・Pre-generation Contract が skill-writing-guide に整備済み。ただし "What NOT to write"（マニュアル化の避け方）の明示が不足 |
| 5 | Treat like real users（eval 化・traces 観測） | Partial | session-observer / trace-store / autoevolve-core は存在するが、friction-events → eval loop への接続が自動化されていない |

## Already Strengthening Analysis (Pass 2: 強化チェック)

| # | 既存の仕組み | 記事が示す弱点 | 強化案 | 判定 |
|---|---|---|---|---|
| S1 | skill-writing-guide（DBS rubric, Atomic, Pre-gen Contract） | "Onboarding not manuals" の概念が明示されていない。What to write / What NOT to write の区別なし | `skill-writing-guide` に "Onboarding not manuals" セクションと Good/Bad 例を追加 | 強化可能 |
| S2 | autoevolve / improve-policy | friction-events.jsonl → eval 化の接続が manual トリガー依存 | `improve-policy.md` に "Friction → Eval Loop" セクション追加（failure-clusters 自動参照、良い挙動 eval 化） | 強化可能 |
| S3 | subagent-delegation-guide | Intentional Restriction（何をあえて制限するか）の明文化なし | `subagent-delegation-guide.md` に Capability Restriction Policy セクション追加 | 強化可能 |
| S4 | wrapper 設計思想 | wrapper vs raw の判断基準が未文書化 | `wrapper-vs-raw-boundary.md` 新規作成（判断マトリクス・既存棚卸し・チェックリスト） | 強化可能 |

## Phase 2.5 Refine 結果

### Codex 批評の要点

- 評価軸を「認知負荷・継続性・失敗時の復元速度」にリフレームすべき
- **#5 Weekly traces hour は個人 harness では dead weight** — チームで非同期観察するための仕組みが、一人運用では逆にコストになる。不採用が正解
- **#2 の厚い wrapper は self-use では合理化できる** — 安全性・再現性・好みの固定化のために wrapper を使う選択は正当。ただし「どこまで raw か」の意識的な選択が重要
- #2 は文書強化ではなく control plane の設計問題。#1 と不可分 — Capability Parity ではなく Intentional Restriction が正解
- 優先度: **#2 (wrapper-vs-raw 境界明文化) + #5 の限定版（friction → eval loop 自動化）のみ**

### Gemini 周辺知識

- **業界トレンド**: PostHog の raw 志向 ⇔ 業界は Agentic API（高抽象化）方向（Linear API、Vercel Generative UI、Figma AI-ready design system）。両極端の間で意識的選択が必要
- **Lost in the Middle (arXiv:2307.03172)**: context 詰め込みの弱点。Front-load (#3) の過剰適用はむしろ degradation を招く可能性。既存の Progressive Disclosure は正しいアプローチ
- **OWASP LLM08 Excessive Agency**: #1 (API parity) の無制限実装は LLM08 リスクを高める。Intentional Restriction が安全性の観点からも正しい
- **類似事例**: PostHog (raw/executeSql), Linear (高抽象), Anthropic Tool Characterization, MCP 標準化方向 — wrapper vs raw は業界未解決の設計問題
- **Replit Agent**: skill/context のオンボーディング設計が agent 生産性に直結することを実証

## Integration Decisions

### Gap / Partial

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| 2 | Wrapper vs raw boundary 明文化 | 採用 | 既存設計の意識的選択を文書化。判断マトリクスとして再利用可能 |
| 5 | Friction → Eval loop 接続（限定版） | 採用 | friction-events.jsonl は存在するが eval 化の接続が欠如。Weekly traces hour は不採用 |

### Already 強化

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| S1 | skill-writing-guide "Onboarding not manuals" 追加 | 採用 | What NOT to write + Lego 比喩追加で既存 guide を強化 |
| S2 | improve-policy Friction → Eval loop セクション追加 | 採用 | autoevolve との接続を明文化 |
| S3 | subagent-delegation-guide Capability Restriction Policy 追加 | 採用 | OWASP LLM08 対応と合わせて整理 |
| S4 | Skill Audit Policy 追加（skill-writing-guide） | 採用 | 既存 61 skills の audit 用象限分類・Manual 度スコアリング |

## Plan

### Task 1: wrapper-vs-raw-boundary.md 新規作成
- **Files**: `references/wrapper-vs-raw-boundary.md`
- **Changes**: wrapper 判断マトリクス（安全性・再現性・認知負荷軸）、既存 wrapper 棚卸し表、チェックリスト
- **Size**: S

### Task 2: subagent-delegation-guide に Capability Restriction Policy 追加
- **Files**: `references/subagent-delegation-guide.md`
- **Changes**: Intentional Restriction の方向性、OWASP LLM08 リスク明示
- **Size**: S

### Task 3: improve-policy に Friction → Eval Loop セクション追加
- **Files**: `references/improve-policy.md`
- **Changes**: failure-clusters 自動参照、良い挙動 eval 化フロー。Weekly traces hour 不採用宣言
- **Size**: S

### Task 4: skill-writing-guide "Onboarding not manuals" 追加
- **Files**: `skills/skill-creator/instructions/skill-writing-guide.md`
- **Changes**: "Onboarding not manuals" + "What to write / What NOT to write" + Good/Bad 例
- **Size**: S

### Task 5: skill-writing-guide Skill Audit Policy セクション追加
- **Files**: `skills/skill-creator/instructions/skill-writing-guide.md`
- **Changes**: 象限分類（raw/onboarding/manual/dead weight）、Manual 度スコアリング基準
- **Size**: S

### Task 6: 本レポート保存
- **Files**: `docs/research/2026-04-11-posthog-agent-first-rules-analysis.md`
- **Changes**: 本ファイル
- **Size**: S

### Task 7: MEMORY.md 更新
- **Files**: `docs/agent-memory/MEMORY.md` (実体: `.claude/projects/.../memory/MEMORY.md`)
- **Changes**: 外部知見統合済みセクションに 1 行ポインタ追加
- **Size**: S

---

## 実行済みタスク（セッション内完了）

ユーザーの選択（T1〜T5 + T6 + T7 全採用、同一セッション S-M 規模）に基づき実行済み:

- **T1**: `references/wrapper-vs-raw-boundary.md` 新規作成（wrapper 判断マトリクス、既存棚卸し表、チェックリスト）
- **T2**: `references/subagent-delegation-guide.md` に Capability Restriction Policy セクション追加（OWASP LLM08 リスク、restriction 方向性）
- **T3**: `references/improve-policy.md` に Friction → Eval Loop セクション追加（failure-clusters 自動参照、良い挙動 eval 化、weekly traces hour 不採用宣言）
- **T4**: `skills/skill-creator/instructions/skill-writing-guide.md` に "Onboarding not manuals" + "What to write / What NOT to write" + Good/Bad 例追加
- **T5**: 同ファイルに Skill Audit Policy セクション追加（象限分類、Manual 度スコアリング）
- **T6**: 本レポート（このファイル）
- **T7**: MEMORY.md に 1 行ポインタ追加

---

## 取り込まなかった内容

- **Weekly traces hour (PostHog #5)** — 個人 harness では dead weight。Codex 批評に従い不採用
- **既存 61 skills の rewrite** — audit policy のみ追加。実 audit は将来の `/skill-audit` に委譲
- **wrapper stack の実コード変更** — 思想の明文化のみ。refactor は今回スコープ外

---

## 今後のアクション（フォロー）

- 次回 skill 追加時に `wrapper-vs-raw-boundary.md` のチェックリストを self-check で使う
- `/improve` 実行時に friction-to-eval-loop policy を試す
- 3 ヶ月後に skill audit を `/skill-audit` で実行（象限分類実データ収集）

---

## 参考リンク

- 記事: https://posthog.com/blog/agent-first-rules (posthog.com)
- 関連論文: arXiv:2307.03172 (Lost in the Middle)
- OWASP LLM08: Excessive Agency
- 関連プラン: MEMORY.md 参照
