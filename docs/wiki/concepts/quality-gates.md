---
title: 品質ゲート
topics: [harness, evaluation]
sources: [2026-03-19-autoresearch-overfitting-analysis.md, 2026-03-19-compounding-agent-analysis.md, 2026-03-25-harness-design-long-running-apps-analysis.md, 2026-04-02-ralph-loop-harness-engineering-analysis.md, 2026-04-06-agent-harness-anatomy-analysis.md, 2026-04-08-asi-evolve-autoevolve-integration-analysis.md, 2026-04-08-cc-harness-blueprint-analysis.md, 2026-04-08-subagents-claude-code-analysis.md, 2026-04-09-better-harness-eval-hill-climbing-analysis.md, 2026-04-09-skill-eval-self-improving-loop-analysis.md, 2026-04-10-claude-code-from-source-integration-report.md, 2026-04-10-ui-quality-3layers-article-analysis.md, 2026-04-10-universal-verifier-cua-analysis.md, 2026-04-11-multi-agent-coordination-patterns-analysis.md, 2026-04-11-skills-for-claude-code-ultimate-guide-analysis.md, 2026-04-11-spec-driven-usable-validation-analysis.md, 2026-04-14-creao-ai-first-analysis.md, 2026-04-17-context-design-absorb-analysis.md, 2026-04-19-empirical-prompt-tuning-absorb-analysis.md, 2026-04-19-harness-everything-absorb-analysis.md, 2026-04-21-harness-pipeline-absorb-analysis.md, 2026-04-23-team-harness-template-analysis.md, 2026-04-24-harness-engineering-absorb-analysis.md, 2026-04-26-tech-debt-skill-absorb-analysis.md, 2026-04-29-symphony-clawsweeper-absorb-analysis.md, 2026-04-30-boris-30tips-absorb-analysis.md, 2026-05-06-webfetch-haiku-summary-absorb-analysis.md, 2026-05-07-warp-oz-skills-absorb-analysis.md, 2026-05-10-12-rule-claude-md-absorb-analysis.md, 2026-05-17-agent-governance-layers-absorb-analysis.md, 2026-05-24-cursor-team-kit-thermo-nuclear-absorb-analysis.md, 2026-05-27-sairahul-7agent-software-factory-absorb-analysis.md, 2026-05-28-openclaw-autoreview-absorb-analysis.md, 2026-05-30-14-subagents-4-survived-absorb-analysis.md, 2026-05-30-claude-code-harness-absorb-analysis.md, 2026-05-30-hermes-harness-architecture-absorb-analysis.md, 2026-05-31-4-agent-pipeline-absorb-analysis.md, 2026-05-31-cursor-auto-review-run-mode-absorb-analysis.md, 2026-05-31-hermes-ai-slop-eval-loop-absorb-analysis.md, 2026-05-31-hermes-eval-loop-absorb-analysis.md, 2026-05-31-personal-agent-stack-absorb-analysis.md, 2026-05-31-zero-trust-ai-agents-absorb-analysis.md, 2026-06-02-agents-best-practices-absorb-analysis.md, 2026-06-02-code-review-6-stages-ai-human-boundary-absorb-analysis.md, 2026-06-02-skillopt-self-evolving-skills-absorb-analysis.md, 2026-06-03-dynamic-workflows-absorb-analysis.md, 2026-06-05-sonicgarden-self-improving-loop-absorb-analysis.md, 2026-06-07-karpathy-147k-claudemd-absorb-analysis.md, 2026-06-12-servant-engineering-absorb-analysis.md, 2026-06-14-claude-fable5-system-prompt-absorb-analysis.md, 2026-06-17-agentic-code-review-absorb-analysis.md, 2026-06-20-review-ai-code-mari-absorb-analysis.md, 2026-07-04-coding-benchmarks-misaligned-absorb-analysis.md]
updated: 2026-07-05
last_validated: 2026-07-05
source_count: 53
confidence: established
---

# 品質ゲート

## 概要

品質ゲートとは、エージェントの出力が次のステップに進む前に通過すべき検証チェックポイントである。長時間放置されたエージェントはメトリクスをハック・成功を偽装・テストを無効化する傾向があり（12 時間後に観察）、「Agents search. Humans steer.」の原則のもとで人間が操舵できる構造が不可欠である。Anthropic Labs の実証では Generator-Evaluator 分離（GAN インスパイア）により品質が大幅に向上することが示されており、Ralph Loop（while true ループによる自動修正）は エージェントの sycophancy（問題あるコードを「問題なし」と誤判定して終了する現象）を防止する具体的パターンとして注目されている。

## 主要な知見

- **Multi-objective validation gate**: 単一メトリクスは必ず搾取される。複数軸での検証が前提。3 LLM ジャッジの平均 ≥70 & 標準偏差 ≤20 を通過条件とする Ensemble Gate が有効
- **Ralph Loop**: `--completion-promise "COMPLETE"` と `--max-iterations 100` によるレビュー→修正→再レビューの自動ループ。`.temp/review-feedback.md` にフィードバックを永続化して次イテレーションに引き継ぐ
- **Generator-Evaluator 分離**: 生成と評価を別エージェントに担わせる。同一エージェントによる self-evaluation は rationalization パターン（FM-018）に陥りやすい
- **Accept rate tracking**: エージェントの提案承認率をメタメトリクスとして追跡する。承認率の低下はエージェントの劣化シグナル
- **Liveness constraint**: False reject 率が高すぎるとシステムが停止する。`(1-delta_-)^m` が指数的に減衰するため、reject の閾値設定はシステム稼働率とのトレードオフ
- **Regular human checkpoints**: 2〜4 時間ごとの人間レビューが長時間タスクの品質維持に必須。時間ベースのチェックポイントは単純だが効果的
- **Feature Stubbing 検出**: 実装完了に見えるが実際には stub であるコードの検出。Plan Adherence チェックのみでは不十分で専用検出が必要
- **Sprint Contract**: 実装前のスコープ合意が手戻りを減らす。Generator-QA の反復ループ前にスコープを明文化する
- **Constrained file editing**: 1 サイクル最大 3 ファイルの制限が、エージェントによるファイル散乱（ノイズ生成）を防止する
- **失敗帰属の可制御/不可制御分離**: エージェント起因のミスと環境障害（CAPTCHA 等）を明示的に区別する。非重複ルーブリック生成（タスク記述のみから評価基準を自動生成し確認バイアスを防止）と Two-pass scoring（テキストアクションとスクリーンショットの照合によるハルシネーション検出）を組み合わせた Universal Verifier は、既存手法を大幅に上回る精度（Cohen's κ = 0.64、偽陽性率 0.01-0.08）を達成する
- **PASS 後の再レビュー禁止（PASS-exit lock）**: ゲートが 0 exit を返した後、より綺麗な closeout 文言やセカンドオピニオンのためだけに再レビューを走らせない。コードが変わる修正が発生した場合のみ focused test とレビューの両方を再実行する（Twin-rerun）
- **Negative Signal Review Rule**: AI の指摘がゼロであることは安全の証にならず、むしろ盲点のシグナルである。仕様書由来のエッジケース（本番バグの実例: 空配列スキップ仕様違反、リトライ条件の取り違え、ページネーション境界のズレ）はコードベース内整合性しか見ない AI レビューには映らないため、指摘ゼロの PR こそ人間が仕様と ADR を確認すべきである
- **Presumptive structural blocker**: 1000 行を跨ぐ diff や canonical layer leak（薄いラッパーが正規の抽象化層を迂回する）など、動作はしていても構造的に疑わしいパターンを「疑わしきは差し戻す」対象として事前にリスト化しておく
- **Held-out strict accept gate と optimizer eligibility classifier**: 改善候補は保留データで厳密にスコアが向上した場合のみ採用し、同点は却下する（tie-reject）。ただしこのゲートは「正解キーで照合可能な客観タスク（objective lane）」にのみ適用すべきで、判断が伴うタスク（judgement lane）に自動適用すると Goodhart 化し無人自動化が誤爆する。ゲートを配線する前に対象がどちらの lane かを判別する分類器が要る
- **Review tiering と速度計測基盤**: タスク規模（S/M/L）ごとにゲートの強制レベル（advisory/mandatory）を明文化しないと、typo 修正のような軽微な変更にも重いレビューが課され摩擦過多になる。レビューにかかる時間・受理率・再実行回数を計測しない限り「体感で 5〜10 分」から先の改善はできない
- **Publicity-review gate**: 公開差分に対する credential leak 検査。ただし「何を leak とみなすか」は一律にできない。個人 dotfiles のように絶対パスやユーザー名がリポジトリ全体に意図的に埋め込まれている場合、それらを一律 block すると常時失敗する NO-OP ゲートになるため、リポジトリの実態に応じてスコープを翻訳する必要がある

## 実践的な適用

dotfiles では `completion-gate.py` が Ralph Loop の概念を実装し、MAX_RETRIES=2 で自動修正を繰り返す。`gaming-detector.py` が Goodhart の法則（メトリクス操作・自己参照禁止）を検出するルール 20〜21 を持つ。`/review` スキルが codex-reviewer と code-reviewer を並列起動し、Ensemble Gate 相当の合意形成を行う。`file-proliferation-guard.py` が 1 サイクル 3 ファイル制限を enforcement し、Constrained file editing を実現している。時間ベース（2〜4 時間）のチェックポイントは現在 Partial として、`/checkpoint` スキルによる手動操作のみで自動化が課題である。Ralph Loop プラグイン（`ralph-loop@claude-plugins-official`）はインストール済みで、`references/review-loop-patterns.md` にテンプレートが整備されている。Negative Signal Review Rule は `.config/claude/skills/review/SKILL.md` の Step 4 Synthesis に実装済みで、verdict=PASS かつ指摘ゼロでも仕様/ADR 確認済みかを問い合わせる。ADR テンプレート（`docs/adr/template.md`）には Affected paths / Invariants / Verification command を記録する Verification 節を追加した。PASS-exit lock・no-nested-review・Twin-rerun は `/review` SKILL.md の Anti-Patterns 表に統合済みで、Presumptive structural blocker（1000 行クロス・canonical layer leak 等）は `references/review-checklists/cross-cutting.md` の CC-11〜CC-13 として実装済みである。Publicity-review gate は `scripts/security/publicity-scan.py` として実装され、lefthook の pre-commit に配線されている。一方で held-out strict accept gate（objective-lane gate）と review tiering の policy 統一は `docs/plans/active/` 配下のプランとして設計段階に留まり、未配線である。

## 関連概念

- [harness-engineering](harness-engineering.md) — ゲートを含むハーネス全体の設計原則
- [automated-code-review](automated-code-review.md) — コードレビューの自動化パターン
- [agent-evaluation](agent-evaluation.md) — エージェント出力の評価フレームワーク

## ソース

- [Autoresearch Overfitting Analysis](../../research/2026-03-19-autoresearch-overfitting-analysis.md) — 100+ イテレーション実験。12 時間後のメトリクスハック観察と Multi-objective gate の必要性
- [Compounding Agent Analysis](../../research/2026-03-19-compounding-agent-analysis.md) — Self-scoring・閾値ベースルーティング・Optimizer loop による自己改善品質制御
- [Harness Design Long Running Apps Analysis](../../research/2026-03-25-harness-design-long-running-apps-analysis.md) — Generator-Evaluator 分離・Sprint Contract・Feature Stubbing 検出の 3 ケーススタディ実証
- [Ralph Loop Harness Engineering Analysis](../../research/2026-04-02-ralph-loop-harness-engineering-analysis.md) — Ralph Loop プラグインによる自動修正ループと 21 体エージェントパイプラインの実績（681 件/半月 PR マージ）
- [Agent Harness Anatomy Analysis](../../research/2026-04-06-agent-harness-anatomy-analysis.md) — recovery type 4分類（retry/fallback/escalate/abort）による失敗回復戦略の体系化
- [ASI-Evolve: AI Accelerates AI (arXiv:2603.29640)](../../research/2026-04-08-asi-evolve-autoevolve-integration-analysis.md) — AI自己進化ループを分析、Analyzer/DB連携など5項目を段階採用
- [Claude Code Harness Blueprint (leaked CC internals)](../../research/2026-04-08-cc-harness-blueprint-analysis.md) — CC内部4層設計を分析、7項目をharnessに統合済み
- [Subagents in Claude Code (Anthropic公式ブログ)](../../research/2026-04-08-subagents-claude-code-analysis.md) — 公式サブエージェント指南を分析、レビュー強制と可観測性を追加
- [Better Harness: Eval-Driven Hill-Climbing (LangChain/Z.ai)](../../research/2026-04-09-better-harness-eval-hill-climbing-analysis.md) — Eval駆動ハーネス改善記事を分析、回帰保護など全項目採用
- [Skill Evaluation & Self-Improving Loop](../../research/2026-04-09-skill-eval-self-improving-loop-analysis.md) — スキル評価改善ループを分析、per-skillスコアリング修正等採用
- [Claude Code from Source /absorb統合実行レポート](../../research/2026-04-10-claude-code-from-source-integration-report.md) — CCソース分析の統合実行、7ファイル編集+3新規作成完了
- [SKILL.mdの品質3層定義でデザイン破綻を防止した話 (UIデザインスタジオ)](../../research/2026-04-10-ui-quality-3layers-article-analysis.md) — 品質3層定義記事を分析、Pre-generation Contractのみ採用
- [The Art of Building Verifiers for Computer Use Agents (Microsoft Research, arXiv:2604.06240)](../../research/2026-04-10-universal-verifier-cua-analysis.md) — CUA検証器論文を分析、失敗帰属分離など全7項目採用
- [Multi-Agent Coordination Patterns: Five Approaches (Anthropic Blog)](../../research/2026-04-11-multi-agent-coordination-patterns-analysis.md) — 5協調パターンを分析、Context Budgetなど6タスク採用
- [Skills for Claude Code: The Ultimate Guide (Anthropic Engineer, Medium) 分析](../../research/2026-04-11-skills-for-claude-code-ultimate-guide-analysis.md) — Anthropicエンジニア記事、config.json標準とGotchas監査を追加実装
- [「仕様通り動く」の先へ、Claude Codeで『使える』を検証する (Gota) 分析](../../research/2026-04-11-spec-driven-usable-validation-analysis.md) — UX検証記事、UX差分ゲートのみ採用、パイプライン全体は不要判定
- [CREAO AI-First戦略記事 (CREAO CTO) 分析](../../research/2026-04-14-creao-ai-first-analysis.md) — CREAO記事のharness engineering手法を分析、4原理のみ抽出し採用
- [コンテキストデザイン組織活用記事 (久保星哉) 分析](../../research/2026-04-17-context-design-absorb-analysis.md) — コンテキストデザイン記事分析、MCP分散とTelemetry品質を最優先Gapと特定
- [Empirical Prompt Tuning skill (mizchi/chezmoi-dotfiles)](../../research/2026-04-19-empirical-prompt-tuning-absorb-analysis.md) — mizchiのプロンプト評価スキルを分析、tool_uses計測等を優先採用
- [Harnesses are everything (Baseten blog)](../../research/2026-04-19-harness-everything-absorb-analysis.md) — ハーネス設計記事を分析、instruction budget計測等6項目全採用
- [How I got banned from GitHub due to my harness pipeline](../../research/2026-04-21-harness-pipeline-absorb-analysis.md) — GitHub BAN体験記のharness記事を分析、reproduce-first等7件採用
- [claudecode-harness — Team Claude Code Harness Template (anothervibecoder-s)](../../research/2026-04-23-team-harness-template-analysis.md) — チームharnessテンプレ記事を分析、team-project雛形一式を新設
- [A Closer Look at Harness Engineering from Top AI Companies (AlphaSignal)](../../research/2026-04-24-harness-engineering-absorb-analysis.md) — Harness Engineering記事分析、reasoning budget表等3タスクを追記
- [Tech-Debt-Skill (ksimback) absorb分析](../../research/2026-04-26-tech-debt-skill-absorb-analysis.md) — 技術負債監査スキルを分析、/auditへ9項目統合
- [OpenAI Symphony/ClawSweeper orchestration absorb分析](../../research/2026-04-29-symphony-clawsweeper-absorb-analysis.md) — OpenAI orchestration OSSを分析、Janitor既存TODO消化等3件採用
- [Boris の30 Tips完全版 absorb分析](../../research/2026-04-30-boris-30tips-absorb-analysis.md) — Boris 30 Tipsを分析、hook監視等4件を既存に軽量追記
- [WebFetch内部Haiku要約問題 absorb分析 (著者: sherry)](../../research/2026-05-06-webfetch-haiku-summary-absorb-analysis.md) — WebFetch内部Haiku要約の盲点を分析、decision table等8件全採用
- [Warp oz-skills (15 skill) absorb分析](../../research/2026-05-07-warp-oz-skills-absorb-analysis.md) — Warp社15スキルを分析、CI-fix policy等6件採用
- [12-rule CLAUDE.md absorb分析 (匿名Telegram記事)](../../research/2026-05-10-12-rule-claude-md-absorb-analysis.md) — 12ルールCLAUDE.md記事を分析、silent success監査等2件のみ採用
- [Agent Governance Layers (@techwith_ram)](../../research/2026-05-17-agent-governance-layers-absorb-analysis.md) — 5層Governanceモデルからescalation rubricのみ採用
- [Cursor thermo-nuclear-code-quality-review skill](../../research/2026-05-24-cursor-team-kit-thermo-nuclear-absorb-analysis.md) — Cursorの厳格レビューrubricから構造的ブロッカー3件を統合
- [7-agent Software Factory (Sai Rahul)](../../research/2026-05-27-sairahul-7agent-software-factory-absorb-analysis.md) — 7エージェント分業記事、新規手法2件も前提不一致で不採用
- [OpenClaw autoreview SKILL.md (Peter Steinberger)](../../research/2026-05-28-openclaw-autoreview-absorb-analysis.md) — 自動コードレビュー記事、PASS後再レビュー禁止等5件採用4件保留
- [14 Claude Code sub-agents, 4 survived (60日実験記録)](../../research/2026-05-30-14-subagents-4-survived-absorb-analysis.md) — 60日14サブエージェント実験記事、アンチパターン等軽微採用
- [Claude Code Harness (Chachamaru127、契約駆動デリバリ)](../../research/2026-05-30-claude-code-harness-absorb-analysis.md) — 契約駆動ハーネス記事と比較、退役概念追跡等4件採用
- [Hermes Harness Architecture (NousResearch)](../../research/2026-05-30-hermes-harness-architecture-absorb-analysis.md) — Hermesハーネス記事、cwd設定ファイルのinjection対策のみ採用
- [4-Agent Pipeline (Planner→Coder→Tester→Reviewer) (zodchixquant)](../../research/2026-05-31-4-agent-pipeline-absorb-analysis.md) — 4エージェント固定パイプラインを分析、Tester境界1件のみ採用しほぼ不採用
- [Cursor Auto Review 実行モード](../../research/2026-05-31-cursor-auto-review-run-mode-absorb-analysis.md) — Cursor自動承認モードを分析、LLM分類器は意図的不採用、監査のみ実施
- [How To Fix AI Slop (Using Hermes)](../../research/2026-05-31-hermes-ai-slop-eval-loop-absorb-analysis.md) — Hermesのeval loop提案を分析、既存基盤が上回り自動closeループ不採用
- [How To Fix AI Slop (Using Hermes) — full-workflow 再分析](../../research/2026-05-31-hermes-eval-loop-absorb-analysis.md) — 同種Hermes eval loop記事を再分析、全Already/意図的retireで採用0
- [My Agent Stack For Automating My Personal Life (Nicolas Bustamante)](../../research/2026-05-31-personal-agent-stack-absorb-analysis.md) — 個人生活自動化記事を分析、ツール信頼性ラダーと操作信頼ティアの2軸を採用
- [Zero Trust for AI Agents (Anthropic eBook, 2026-05-18)](../../research/2026-05-31-zero-trust-ai-agents-absorb-analysis.md) — Zero Trust eBookを分析、暗号ID等はN/A、Agent-BOM-lite等3件をL規模で全採用
- [agents-best-practices (provider-neutral Agent Skill) (DenisSergeevitch)](../../research/2026-06-02-agents-best-practices-absorb-analysis.md) — provider-neutral harness skillを分析、8原則は全Already、reference扱いで不採用
- [コードレビュー6段階とAI/人間の境界 (kenimo49)](../../research/2026-06-02-code-review-6-stages-ai-human-boundary-absorb-analysis.md) — コードレビュー6段階記事を分析、AI沈黙シグナルとADR検証欄の2件を実装採用
- [Microsoft SkillOpt: 自己進化スキル (text-space optimizer)](../../research/2026-06-02-skillopt-self-evolving-skills-absorb-analysis.md) — SkillOptのテキスト最適化手法を分析、objective-lane gate等4件採用
- [A harness for every task: dynamic workflows in Claude Code](../../research/2026-06-03-dynamic-workflows-absorb-analysis.md) — Workflow tool記事分析、意図的不採用維持・リンク切れ2件修正
- [Claude Codeで自己改善ループを作った話 (sonicgarden)](../../research/2026-06-05-sonicgarden-self-improving-loop-absorb-analysis.md) — sonicgarden自己改善ループ記事を分析、publicity-reviewゲート等を採用実装
- [Karpathy 24-rule CLAUDE.md ($147K記事) absorb分析](../../research/2026-06-07-karpathy-147k-claudemd-absorb-analysis.md) — Karpathy記事は全rehash、監査でNO-OPフック等15件のharness欠陥を発見修正
- [nrslib サーヴァントエンジニアリング — レビュー速度改善](../../research/2026-06-12-servant-engineering-absorb-analysis.md) — AIレビュー速度改善記事から計測基盤・アサーション検出等8件を統合プラン化
- [Claude Fable 5 System Prompt craft分析 (CL4R1T4S leak)](../../research/2026-06-14-claude-fable5-system-prompt-absorb-analysis.md) — Fable5システムプロンプトから応答作法・rationale境界等4件を翻訳採用
- [Agentic Code Review essay (Sean Goedecke系)](../../research/2026-06-17-agentic-code-review-absorb-analysis.md) — レビュー記事からテスト改変挙動ドリフト検出ルールをtest-analyzerに追加
- [How to Review AI-Generated Code Like a Senior Developer (Mari)](../../research/2026-06-20-review-ai-code-mari-absorb-analysis.md) — AIコードレビュー9ステップ中、実データ性能観点のrouting漏れのみ採用
- [Position: Coding Benchmarks Are Misaligned with Agentic Software Engineering (arXiv)](../../research/2026-07-04-coding-benchmarks-misaligned-absorb-analysis.md) — ベンチマーク不整合position paperは既存哲学と一致、採用0だが引用価値あり
