---
name: openai-frontend-prompt-workflow
description: Use when the user wants reusable GPT-5.4 frontend prompt templates, wants OpenAI frontend prompting guidance operationalized, or wants Codex to ask for missing inputs before drafting a frontend prompt.
platforms: [agents, codex]
---

# OpenAI Frontend Prompt Workflow

OpenAI の frontend blog と公開 `frontend-skill` を、Codex で再利用しやすい workflow に落とす。

## When To Use

- GPT-5.4 向け frontend prompt を再利用したい
- landing page / app / dashboard 用の prompt template を作りたい
- OpenAI の frontend guidance を実務向けに整形したい
- 必要情報が欠けているので、先に入力を聞き返してから prompt を組み立てたい

## Sources Of Truth

- OpenAI blog: `Designing delightful frontends with GPT-5.4`
- 公開 `frontend-skill`
- 必要なら `openai-docs` skill と OpenAI docs MCP

詳細テンプレートは `references/templates.md` を使う。

## Workflow

1. ユーザーの目的を分類する。
   - `landing page`
   - `app / dashboard`
   - `image-led landing page`
   - `which template should I use?`
2. 必須入力が揃っているか確認する。
3. 足りない場合は、まず聞き返す。
4. 揃ったら、最も近い template を選ぶ。
5. 必要なら user 向けに短縮版と完全版を両方出す。
6. 公式由来の制約と、自分の再構成を混同しない。

## Pairing Rule

- この skill は prompt 設計と intake に使う
- 実際に UI を実装する段階では、可能なら `frontend-skill` と組み合わせる
- 役割分担:
  - `openai-frontend-prompt-workflow`: 何をどう頼むかを固める
  - `frontend-skill`: 実装中の composition, imagery, motion, hierarchy を強く保つ
- ユーザーが「prompt がほしい」のか「実装してほしい」のかで、どちらを前面に出すかを切り替える

## Codex Settings Rule

- Codex の通常設定に反映する場合は、長い prompt 本文を `AGENTS.md` に貼らない。
- runtime guidance は `.codex/AGENTS.md` に短い routing rule として残す。
- reasoning の既定切替は `.codex/config.toml` の `profiles.frontend` に寄せる。
- 詳細な frontend 制約、intake、handoff prompt はこの skill の `references/templates.md` と `frontend-skill` に残す。
- OpenAI 公式記事やモデル guidance を再確認する場合は global `openai-docs` skill と OpenAI docs MCP を使う。

## Ask-Back Rule

以下が欠けている場合は、prompt を書き切る前に簡潔に聞き返す。

- surface type
  - landing page / app / dashboard / mixed
- product context
  - 何の UI か
- brand and audience
  - 誰向けで、どのブランドか
- visual direction
  - style / palette / composition / mood
- content inputs
  - 実 copy、goal、CTA、必須 section
- implementation target
  - ChatGPT / Codex / Responses API

質問は必要最小限にまとめる。まずは次の 4 つを優先する。

1. 何を作る prompt ですか。`landing page`、`app`、`dashboard` のどれですか。
2. 対象の product / brand と audience は何ですか。
3. visual direction はありますか。なければ `style / palette / mood` だけでもください。
4. 実際に使う copy、goal、CTA はありますか。

## Output Modes

- `short`
  - そのまま貼れる prompt だけ返す
- `full`
  - prompt + checklist + ask-back gap を返す
- `compare`
  - official-derived constraints と custom additions を分けて返す

ユーザー指定がなければ `full` を使う。

## Guardrails

- OpenAI の prompt 例や skill を「そのまま配布されている一本の公式テンプレート」と言わない
- 公式由来の hard rules を落とさない
- landing page と app UI を混ぜない
- 実 copy がないときは placeholder 前提であることを明示する
- 必要なら `Playwright` による verification を含める

## Recommended Deliverables

- 最適な template 1 本
- 必要なら短縮版 1 本
- 欠けている入力の list
- 公式由来の制約 list
- 実装に進むなら `frontend-skill` へ渡す handoff prompt

## Anti-Patterns

- いきなり長い prompt を出して、必要入力の欠落を放置する
- landing page に app UI の utility-copy rule を混ぜる
- app UI に hero-heavy な marketing structure を強制する
- `full-bleed hero`、`cardless default`、`brand first` を落とす
