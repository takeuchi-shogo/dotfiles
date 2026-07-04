---
title: スキル設計
topics: [skill]
sources: [2026-03-18-skill-lessons-analysis.md, 2026-03-24-claude-skills-2.0-article-analysis.md, 2026-03-30-cc-skills-golang-analysis.md, 2026-04-02-master-claude-skills-module2-analysis.md, 2026-04-03-grill-me-skill-viral-analysis.md, 2026-04-10-notebooklm-claude-extend-sessions-analysis.md, 2026-04-09-12-claude-patterns-analysis.md, 2026-04-09-30-claude-prompts-analysis.md, 2026-04-09-paper-analysis-prompts-analysis.md, 2026-04-10-atomic-skills-coding-agents-analysis.md, 2026-04-10-ui-quality-3layers-article-analysis.md, 2026-04-11-posthog-agent-first-rules-analysis.md, 2026-04-11-skills-for-claude-code-ultimate-guide-analysis.md, 2026-04-12-tan-thin-harness-fat-skills-analysis.md, 2026-04-14-karpathy-second-brain-modified-analysis.md, 2026-04-19-empirical-prompt-tuning-absorb-analysis.md, 2026-04-19-gh-skill-cli-analysis.md, 2026-04-19-top67-claude-skills-analysis.md, 2026-04-21-obsidian-claudecode-absorb-analysis.md, 2026-04-24-google-skills-adk2-absorb-analysis.md, 2026-04-26-skill-md-15min-guide-absorb-analysis.md, 2026-04-29-claude-skills-six-laws-absorb-analysis.md, 2026-04-29-mattpocock-skills-absorb-analysis.md, 2026-04-30-claude-api-skill-absorb-analysis.md, 2026-05-02-30-subagents-2026-absorb-analysis.md, 2026-05-06-100-skills-best6-absorb-analysis.md, 2026-05-07-warp-oz-skills-absorb-analysis.md, 2026-05-09-skill-inventory-vs-usage.md, 2026-05-13-grown-claude-code-metabolism-absorb-analysis.md, 2026-05-23-anthropic-complete-guide-building-skills-absorb-analysis.md, 2026-05-25-khairallah-50-prompts-absorb-analysis.md, 2026-05-31-personal-agent-stack-absorb-analysis.md, 2026-06-02-agents-best-practices-absorb-analysis.md, 2026-06-02-how-to-actually-use-claude-14-steps-absorb-analysis.md, 2026-06-02-skillopt-self-evolving-skills-absorb-analysis.md, 2026-06-02-suzanne-teachback-absorb-analysis.md, 2026-06-05-muse-autoskill-self-evolving-agents-absorb-analysis.md, 2026-06-14-claude-fable5-system-prompt-absorb-analysis.md, 2026-06-17-stop-slop-prose-anti-slop-absorb-analysis.md, 2026-06-18-japanese-tech-writing-absorb-analysis.md, 2026-06-20-knowledge-work-plugins-absorb-analysis.md]
updated: 2026-07-05
last_validated: 2026-07-05
source_count: 41
confidence: established
---

# スキル設計

## 概要

スキルは Claude Code に対して再利用可能な知識・手順・ワークフローをパッケージ化する仕組みである。SKILL.md の metadata 精度がトリガー精度を決定し、Progressive Disclosure（段階的開示）でトークン効率を最適化する。設計の核心は「Claude がすでに知っていることは書かない」という原則にあり、スキル固有のコンテキスト（Gotchas・境界定義・スクリプト）のみを提供する。

## 主要な知見

- **9カテゴリのスキル分類**: Library & API Reference / Product Verification / Data Fetching / Business Process Automation / Code Scaffolding / Code Quality & Review / CI/CD / Runbooks / Infrastructure Operations の9種が実用的な分類軸となる
- **Gotchas セクションが最高価値**: スキル内で最も ROI が高いのは「落とし穴・例外・注意点」のセクション。一般知識ではなく、ドメイン固有の暗黙知を書く
- **description フィールドはトリガー条件を記述する**: 要約ではなく「どのような状況でこのスキルを使うべきか」を書く。`Triggers:` と `Do NOT use for:` の両方を定義して境界を明確にする
- **Lazy-loaded アーキテクチャ**: description（~100トークン）で常時ロード、SKILL.md（~2.5K トークン）はオンデマンドロード、reference/ で深掘りという3層構造が最適
- **On Demand Hooks**: スキルが active なときのみ有効なフックを定義し、通常実行への副作用を排除する
- **評価駆動の品質管理**: アサーションベースの自動評価（eval-driven）でスキルの効果を定量測定する。cc-skills-golang では 54% → 98%（+44pp）の改善を計測
- **スクリプト委譲**: 計算・ファイル処理・外部連携はスキルから分離したスクリプトに委譲し、SKILL.md は推論の指針に集中させる
- **テリトリー衝突検出**: 複数スキル間でトリガー言語が重複する場合、`/skill-audit conflict-scan` で完全一致・部分包含・排他欠落の3種の衝突を自動検出する
- **Overridable design**: プロジェクト固有のスキルが `supersedes` 宣言によって汎用スキルを上書きできるよう設計する
- **Grill パターン（事前ストレステスト）**: Matt Pocock の grill-me スキルに見られるように、極めてシンプルなプロンプト（「容赦なく全側面を問い詰めろ」+ 決定木走破 + AI推奨回答）が高い効果を発揮する。スキルは複雑である必要はなく、適切な制約を短く記述するだけで十分な場合がある
- **DBS Rubric（Direction/Blueprints/Solutions）**: スキルのリソースを目的別に 3 分類する判断原則。Direction=SKILL.md 本文+instructions/（手順・判断）、Blueprints=references/+assets/（静的参照・テンプレート）、Solutions=scripts/（決定論的処理）。判断を scripts に埋めると柔軟性が落ち、決定論的処理を SKILL.md に書くと再現性が落ちる。Atomic Skill の Self-containment と併せて考えると「1 スキル = 1 Direction + 必要な Blueprints/Solutions の束」と捉えられる
- **スキル設計3原則と構成的汎化**: コーディングエージェント向けの原子スキル研究では、良いスキルは「最小性・自己完結性・独立評価可能性」の3条件を満たすべきとされる。個々のスキルを独立して改善すると、その効果が未見の複合タスクにも転移する（構成的汎化）ことが実証されており、per-skill evaluation の妥当性を裏付ける
- **Recipes, Not Orders + Invert Test**: スキルは「〇〇しろ」という命令ではなく、パラメータ化された method call（レシピ）として設計し、結論ではなく思考プロセスを教える。作成後のセルフチェックとして「エージェントが反対の結論（不採用・却下・別の選択）も導けるか」を検証する Invert Test が、一方向フローや結論の埋め込みを検出する
- **Judgment vs Computation の境界**: スキル内の各判断について、latent（人間的判断が必要）か deterministic（計算・スクリプトで決まる）かを明示的に切り分ける。この境界が曖昧だと、判断をスクリプトに埋めて柔軟性を落としたり、決定論的処理を本文に書いて再現性を落としたりする
- **Setup Config & Persistent State パターン**: スキルが永続設定・状態を持つ場合は `config.json` や `~/.claude/skill-data/{skill}/` のような専用 namespace に分離する標準スキーマを用意する。秘密情報は config.json に書かず `secrets.env` やキーチェーンへ分離する
- **description の定量的トリガー設計**: description が50文字未満だと呼出頻度が3〜5倍下がる、最初の250文字にユースケースを明示する、Out of Scope（使わない条件）を明記した高品質スキルは全体の約70%を占める、といった経験則がある。SKILL.md 本体は500行以内、冒頭50行（entry screen）はトリガー・使い方・次に読むべき参照へのポインタに絞り、詳細は reference に逃がす
- **Pipeline/Guard/Gate デザインパターンと3-arm eval**: 決定的な処理フローを持つスキルは Pipeline（多段階処理でゲートを明示）・Guard（危険操作前の確認）・Gate（外部呼び出し前のバリデーション）の3型に整理できる。品質評価は baseline vs skill の2-arm比較よりも、skill vs terse-instruction vs baseline の3-arm比較がゴールドスタンダードとされ、「スキルなし」だけでなく「簡潔な指示のみ」との比較で真の付加価値を切り分けられる
- **スキルのテキスト最適化と適用境界**: スキル本文（自然言語の指示文）自体を訓練対象として編集する自己進化アプローチ（SkillOpt）では、正解キーが存在し客観的に照合可能なタスク（抽出・分類・構造化生成）に限り、held-out データで厳密な性能向上が確認できた編集のみを採用する（同点は reject）。逆に absorb・review・think のような判断系スキルには「間違ったツール」と位置づけられており、自動最適化の対象を選別する入口分類が前提条件になる

## 実践的な適用

dotfiles リポジトリでは 60+ スキルを `.config/claude/skills/` 以下に管理している。`skill-writing-guide.md` と `skill-writing-principles.md` がスキル作成の規範を定義し、`description-optimization.md` が eval 駆動のトリガー最適化ループを定義している。`/skill-audit` コマンドで全スキルの横断監査（Trigger conflict scan 含む）を実行でき、`skill-suggest.py` フックが実行時にスキルの推薦を行う。skills.sh 経由で 16 の外部スキルもインストール済みである。Invert Test は `skill-writing-principles.md` 原則1の小節として、Judgment vs Computation の境界は `determinism_boundary.md` と DBS Rubric として、negative routing は `skill-conflict-resolution.md` として実装済み。3-arm eval は `skill-creator/scripts/run_eval.sh` と `aggregate.py --three-arm` に、description の字数バジェットは `skill-audit/SKILL.md` の Description Token Tax チェックに組み込まれている。

## 関連概念

- [skill-chaining](skill-chaining.md) — スキルを連鎖させてより複雑なワークフローを構成するパターン
- [claude-code-architecture](claude-code-architecture.md) — スキルが組み込まれる Claude Code 全体のアーキテクチャ
- [context-engineering](context-engineering.md) — Progressive Disclosure とトークン効率最適化の基盤理論
- [pre-generation-contract](pre-generation-contract.md) — 生成前に Must/Important/Optional の義務差を宣言し、生成中に照合できる形で品質基準を SKILL.md に埋め込むパターン。Independent Evaluability の実質化

## ソース

- [Lessons from Building Claude Code: How We Use Skills](../../research/2026-03-18-skill-lessons-analysis.md) — Anthropic 公式の 9 カテゴリ分類と 9 ベストプラクティス。Gotchas・On Demand Hooks・description 最適化を解説
- [How to Build Claude Skills 2.0](../../research/2026-03-24-claude-skills-2.0-article-analysis.md) — Progressive Disclosure・500行上限・負の境界定義のベストプラクティスと dotfiles への適用ギャップ分析
- [cc-skills-golang](../../research/2026-03-30-cc-skills-golang-analysis.md) — Go 開発向けスキル設計。Lazy-loaded atomic skills・eval-driven quality・Ultrathink auto-trigger のパターン
- [Master Claude Skills Module 2](../../research/2026-04-02-master-claude-skills-module2-analysis.md) — scripts/ レイヤー分離・マルチスキルオーケストレーション・リファレンス最適化のアーキテクチャガイド
- [Grill Me Skill Viral](../../research/2026-04-03-grill-me-skill-viral-analysis.md) — シンプルなプロンプトによるプラン・設計のストレステスト。決定木走破 + AI推奨回答パターン
- [NotebookLM Claude セッション拡張分析](../../research/2026-04-10-notebooklm-claude-extend-sessions-analysis.md) — DBS rubric (Direction/Blueprints/Solutions) の明文化。非公式 API 統合の production harness リスク評価と Codex セカンドオピニオンによる 1 項目採用の事例
- [12 Claude Patterns You've Never Tried (@sharbel)](../../research/2026-04-09-12-claude-patterns-analysis.md) — Claude活用12パターンを分析、全項目を既存スキル強化に統合
- [30 Claude Prompts, Workflows & Automations (@eng_khairallah1)](../../research/2026-04-09-30-claude-prompts-analysis.md) — 実務プロンプト30選を分析、決定ジャーナルなど9タスク採用
- [9 Prompts for Academic Paper Analysis (James, Twitter)](../../research/2026-04-09-paper-analysis-prompts-analysis.md) — 学術論文分析9手法を統合、/paper-analysisスキル新設
- [Scaling Coding Agents via Atomic Skills (arXiv:2604.05013)](../../research/2026-04-10-atomic-skills-coding-agents-analysis.md) — 原子スキル分解論文を分析、独立評価可能性など4タスク採用
- [SKILL.mdの品質3層定義でデザイン破綻を防止した話 (UIデザインスタジオ)](../../research/2026-04-10-ui-quality-3layers-article-analysis.md) — 品質3層定義記事を分析、Pre-generation Contractのみ採用
- [PostHog『The golden rules of agent-first product engineering』(Jina Yoon) 分析](../../research/2026-04-11-posthog-agent-first-rules-analysis.md) — PostHog記事、wrapper境界文書化とfriction→evalループを採用
- [Skills for Claude Code: The Ultimate Guide (Anthropic Engineer, Medium) 分析](../../research/2026-04-11-skills-for-claude-code-ultimate-guide-analysis.md) — Anthropicエンジニア記事、config.json標準とGotchas監査を追加実装
- [Garry Tan『Thin Harness, Fat Skills』(Ten Design Principles of Agentic AI Skills) 分析](../../research/2026-04-12-tan-thin-harness-fat-skills-analysis.md) — Tan「Thin Harness Fat Skills」分析、Invocation Pattern等3件を新規実装
- [Modified Karpathy Method セカンドブレイン記事 (Kevin) 分析](../../research/2026-04-14-karpathy-second-brain-modified-analysis.md) — Karpathy法改変記事分析、frontmatterでなく_drafts分離方式で採用
- [Empirical Prompt Tuning skill (mizchi/chezmoi-dotfiles)](../../research/2026-04-19-empirical-prompt-tuning-absorb-analysis.md) — mizchiのプロンプト評価スキルを分析、tool_uses計測等を優先採用
- [GitHub CLI gh skill コマンド changelog 分析](../../research/2026-04-19-gh-skill-cli-analysis.md) — gh skill CLI記事を分析、provenance追記等7項目を採用
- [Top 67 Claude Skills (polydao)](../../research/2026-04-19-top67-claude-skills-analysis.md) — Claude Skills 67選記事を分析、新規2件+既存強化1件のみ採用
- [Obsidian × Claude Code — .claude ディレクトリ設計パターン (@akira_papa_AI)](../../research/2026-04-21-obsidian-claudecode-absorb-analysis.md) — Obsidianのcommands/skills設計を分析、Inbox連携等5タスクを採用
- [google/skills + ADK 2.0 Multi-Agent Orchestration Patterns](../../research/2026-04-24-google-skills-adk2-absorb-analysis.md) — google/skills 13個全採択、ADK 2.0パターンは強化不要と判定
- [SKILL.md 15分ガイド absorb分析 (著者: Nyk)](../../research/2026-04-26-skill-md-15min-guide-absorb-analysis.md) — SKILL.md初級ガイドを分析、成熟済みで不採用と判定
- [Claude Code Skills 6つの設計法則 absorb分析 (zodchiii)](../../research/2026-04-29-claude-skills-six-laws-absorb-analysis.md) — Skill設計6法則を分析、near-miss例等2件を軽量統合
- [mattpocock/skills (28K stars) absorb分析](../../research/2026-04-29-mattpocock-skills-absorb-analysis.md) — mattpocock 5-skillチェーンを分析、HITL/AFKマーカー等2件統合
- [Claude API skill 4社展開 absorb分析 (Anthropic公式)](../../research/2026-04-30-claude-api-skill-absorb-analysis.md) — Anthropic公式アナウンス記事を分析、採用0件で全項目Already
- [30 Claude Code Sub-Agents I Actually Use in 2026 absorb分析](../../research/2026-05-02-30-subagents-2026-absorb-analysis.md) — 30サブエージェント記事を分析、メタ原則2件+強化2件採用
- [I Tried 100+ Claude Code Skills, These 6 Are Best absorb分析](../../research/2026-05-06-100-skills-best6-absorb-analysis.md) — 厳選skill 6選記事を分析、Review独立再現フェーズ等5件採用
- [Warp oz-skills (15 skill) absorb分析](../../research/2026-05-07-warp-oz-skills-absorb-analysis.md) — Warp社15スキルを分析、CI-fix policy等6件採用
- [Skill/Agent Inventory × Usage Cross-Reference レポート](../../research/2026-05-09-skill-inventory-vs-usage.md) — 172スキル/エージェントの使用状況を横断集計、死蔵15件検出
- [育てるClaude Codeから勝手に育つClaude Codeへ (@0xfene)](../../research/2026-05-13-grown-claude-code-metabolism-absorb-analysis.md) — skill代謝記事からGotchas欄と週次friction digestを採用
- [The Complete Guide to Building Skills for Claude (Anthropic公式)](../../research/2026-05-23-anthropic-complete-guide-building-skills-absorb-analysis.md) — 公式Skillsガイドから3-arm eval基盤など5件採用
- [50 Claude Prompts That Replace an Entire Team (Khairallah)](../../research/2026-05-25-khairallah-50-prompts-absorb-analysis.md) — 50プロンプト記事を再検証、初回手抜きを訂正し4件即実装
- [My Agent Stack For Automating My Personal Life (Nicolas Bustamante)](../../research/2026-05-31-personal-agent-stack-absorb-analysis.md) — 個人生活自動化記事を分析、ツール信頼性ラダーと操作信頼ティアの2軸を採用
- [agents-best-practices (provider-neutral Agent Skill) (DenisSergeevitch)](../../research/2026-06-02-agents-best-practices-absorb-analysis.md) — provider-neutral harness skillを分析、8原則は全Already、reference扱いで不採用
- [movez「Claudeの14ステップ活用法」](../../research/2026-06-02-how-to-actually-use-claude-14-steps-absorb-analysis.md) — Claude活用14ステップ記事、既存判断で全手法カバー済み・採用0件
- [Microsoft SkillOpt: 自己進化スキル (text-space optimizer)](../../research/2026-06-02-skillopt-self-evolving-skills-absorb-analysis.md) — SkillOptのテキスト最適化手法を分析、objective-lane gate等4件採用
- [Suzanne teach-back prompt (Anthropic)](../../research/2026-06-02-suzanne-teachback-absorb-analysis.md) — Suzanne teach-backを分析、軽量/teachbackコマンド採用
- [MUSE-Autoskill: Self-Evolving Agents via Skill Lifecycle](../../research/2026-06-05-muse-autoskill-self-evolving-agents-absorb-analysis.md) — MUSE論文のスキル生涯管理を分析、per-skill memoryなど新規性ゼロ採用0件
- [Claude Fable 5 System Prompt craft分析 (CL4R1T4S leak)](../../research/2026-06-14-claude-fable5-system-prompt-absorb-analysis.md) — Fable5システムプロンプトから応答作法・rationale境界等4件を翻訳採用
- [stop-slop: AI tell removal from prose (Hardik Pandya)](../../research/2026-06-17-stop-slop-prose-anti-slop-absorb-analysis.md) — AI臭除去skillからfalse-agency・em-dash回避等をprose.mdに最小追記
- [japanese-tech-writing SKILL (k16shikano)](../../research/2026-06-18-japanese-tech-writing-absorb-analysis.md) — 日本語技術文章規範から論証設計・段落構造等6件をprose.mdに統合
- [Anthropic knowledge-work-plugins (Cowork公式)](../../research/2026-06-20-knowledge-work-plugins-absorb-analysis.md) — Cowork職務別プラグイン集は開発ハーネスとscope不一致、採用0
