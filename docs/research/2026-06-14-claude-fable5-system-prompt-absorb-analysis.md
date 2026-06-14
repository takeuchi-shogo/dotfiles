---
date: 2026-06-14
status: implemented
family: official-system-prompt-craft
family_n: 1
source:
  title: "Claude Fable 5 — System Prompt"
  origin: "elder-plinius/CL4R1T4S (ANTHROPIC/CLAUDE-FABLE-5.md)"
  provenance: "reconstructed leak, unofficial, accuracy not guaranteed"
  type: system-prompt
verification_status: verified
adopted: 4
declined: 11
---

# /absorb — Claude Fable 5 System Prompt（craft reference として）

## Source Summary

Anthropic の claude.ai チャット interface 向け本番システムプロンプト（通称 "Claude Fable 5"）の第三者再構成版。約 67.6KB。product_information / refusal_handling / tone_and_formatting / user_wellbeing / evenhandedness / knowledge_cutoff / memory / artifacts storage / mcp_app_suggestions / computer_use / search_instructions + copyright / image_search の各セクションで構成。

**Saturation Gate**: PASS（新 family `official-system-prompt-craft`, N=1）。既存の Fable 言及（`2026-06-12-fable5-14steps`）は self-evolving agent 構築の cross-family で、公式プロンプトを craft reference として分析する角度は前例なし。

## 品質評価（ユーザー要請）

高品質なのは事実。craft として効いている点:
- 指示を「願望」でなく「判定基準」で書く（検索ルールは決定手続き + 例ごとの Rationale）
- 安全セクションの edge-case 密度（wellbeing が異様に具体的: 氷・輪ゴムは自傷の感覚を再現するので代替提案にしない / NEDA は切断済→Alliance へ）
- positive+negative + rationale のペア、段階的 severity（LIMIT 1/2/3, SEVERE/NON-NEGOTIABLE）、敵対入力への自己防御（Anthropic を騙る末尾タグへの警戒を内蔵）

そのまま移植してはいけない理由:
- monolithic/flat（Progressive Disclosure なし）— 単一チャットプロンプトには最適だが多層 harness には不適合。設計思想が違うだけで両方正しい
- 長さが Fable 級 instruction-follower 前提 — IFScale により小型/agentic モデルでは遵守率が落ちる
- 半分以上が chat 製品/ツール固有（artifacts/computer use/web_search/MCP app）で Claude Code では無意味〜有害
- provenance: 再構成リーク、正確性保証なし、proprietary IP

**最重要の発見**: Fable が**散文（プロンプト）で強制している箇所を、dotfiles は mechanism（hook/deny-rule）で強制している** — `self-check before responding`→completion-gate hook、`hard-limit labels`→git deny-rule。harness 自身の原則「static-checkable rules は mechanism に寄せる」に照らすと、この次元では dotfiles の方が先行。

## Pass 1/2 判定（14 パターン）

「object-level 振る舞いルール (O)」と「meta-level prompt 記述技法 (M)」に分類して照合。

| # | パターン | Pass2 判定 | 根拠 / 既存 |
|---|---|---|---|
| O1 | evenhandedness/steelman | N/A | 政治/倫理討論向け、coding でほぼ発火せず base model 訓練済 |
| O2 | epistemic humility | Already | `templates/claude-md/principles.md`, `rules/common/overconfidence-prevention.md` |
| O3 | anti-sycophancy 鋭利化 | **Adopt** | `references/agency-safety-framework.md` に会話応答作法を追記 |
| O4 | prose-first 出力 | **Adopt（任意・低優先）** | 既存 output style は brevity/caveman で逆方向。optional mode として追加 |
| O5 | 曖昧でもまず答える | N/A（意図的相違） | coding は「推測せず聞く」が正しく、Fable のチャット既定はこのドメインでは誤り |
| O6 | copyright hard-limit | Already/N/A | `/absorb` fetch-policy に faithfulness として存在 |
| O7 | 能力/ツール境界の透明な明示 | Partial（低優先） | Codex が指摘した見落とし。O2 と重複大。今回未着手 |
| M1 | User/Assistant 対話ペア | Already隣接 | M2 が核を被覆 |
| M2 | Good/Bad 併記 | Already | `skill-writing-guide.md`, `feedback_bad_example_pattern` |
| M3 | self-check checklist | **Adopt（判定訂正）** | 「mechanism 完全代替」は誤り→Pre-generation Contract を高stakes skill に selective embed |
| M4 | severity ラベル体系 | Already（mechanism + Must/Important/Optional） | deny-rule + `skill-writing-guide.md:168` の義務 3 層 |
| M5 | inline rationale | **Adopt（境界明文化）** | N/A は行き過ぎ→危険/非直感ルールだけ 1 文 rationale |
| M6 | principle-vs-format 分離 | Partial/Already | `reference_brevity_tradeoff`（ゲート冗長性必須）が核を被覆 |
| M7 | when-to-X 決定表 | Already | `decision-tables-index.md` |

## Phase 2.5 — Codex + Gemini 批評の統合

gate が **私の in-group バイアスを双方向に補正**:
- **O4 を過大評価していた**（Codex）: Gap ではなく既存 minimal/brevity の反対モードが未整理なだけ。`concise.md:41` は技術説明/レビュー/検証で通常文を保持する例外を既に持ち、`output-modes.md:12` に explanatory/learning が既存。→ optional mode 追加・低優先に降格。
- **M3 / M5 を過剰 prune していた**（Codex）: M3 の completion-gate は Stop時/テスト時ゲートで生成中の形式/tone/claim 粒度を拾えない（`completion-gate.py`）→ Pre-generation Contract（`skill-writing-guide.md:164`）は別レイヤーの補完。M5 は短い rationale が遵守率を上げる（`skill-writing-principles.md:6` の既存例外）→ N/A は行き過ぎ。
- **O3 は弱候補で正しいと両者一致**。Gemini は Sharma et al. 2023 を引用し sycophancy 抑制の採用価値を支持。
- **verbatim 移植も「崩す」のと同等に危険**（両者一致）: Gemini が community consensus として Calibration Drift / Security Inheritance（既知 injection 穴の輸入）/ staleness を指摘。Craft vs Text では経験者（Simon Willison, Riley Goodside）は Text をコピーせず Craft を模倣。
- **nuance**: 「推論はプロンプトで移植不可」は概ね正しいが、prose-first には「箇条書きへの逃避を禁じ論理の言語化を強制する」副次効果があり、推論品質に間接的に効く（Gemini）。

**統合結論**: 解は「文言を移植する」でも「アレンジする」でもなく、**移植可能な behavior を harness 自身の vocabulary に翻訳して既存ファイルに小さく足す**こと。これで (a) Fable の calibration に触れない (b) リーク text を埋め込まない（injection/staleness 回避） (c) dotfiles 側 calibration も CLAUDE.md 非汚染で守る。

## 採用（4 件・全て S 規模・CLAUDE.md 非汚染・推論非接触）

| # | ファイル | 変更 |
|---|---|---|
| O3 | `references/agency-safety-framework.md` | 「応答作法（ミス認定・立場保持）」サブセクション追加（事実/影響/次手・過剰謝罪なし・圧力下での立場保持） |
| M5 | `skills/skill-creator/references/skill-writing-principles.md` | Principle 1 の例外を 3 条件（重大/非直感/高コスト）に明文化、IFScale バランスを併記 |
| M3 | `skills/skill-creator/instructions/skill-writing-guide.md` | Pre-generation Contract に「completion-gate との役割分担」note 追加（mechanism 代替ではなく補完、高stakes に selective embed） |
| O4 | `references/personas/output-modes.md` | `prose`（散文優先）optional mode を追加（opt-in 専用、default にしない） |

## 棄却（理由付き・Pruning-First）

O1（N/A: 政治討論向け）/ O2（Already）/ O5（N/A: coding は ask-before-guess が正）/ O6（Already: /absorb fetch-policy）/ O7（Partial: O2 重複、低優先で未着手）/ M1（Already隣接）/ M2（Already）/ M4（Already: mechanism + 義務 3 層）/ M6（Partial/Already: brevity-tradeoff）/ M7（Already: decision-tables-index）。

## 教訓

- **技術名 N/A ≠ 原則 N/A**: chat ツールは N/A でも、能力境界の明示・拒否時の代替提示・過剰謝罪回避・根拠粒度調整は coding agent に効く（Codex 指摘）。
- **「mechanism で代替済」は過剰 prune を生みやすい**: 機械ゲートと生成中 self-check は別レイヤー。代替と補完を区別する。
- **2.5 gate は in-group バイアスを双方向に捕捉した**: 既存を過大評価（O4）も過小評価（M3/M5）も補正。cross-model 批評の実効性の実証。
- **「崩したくない」への正解は verbatim ではなく vocabulary 翻訳**: 公式プロンプトの calibration も自 harness の calibration も守るには、文言を移さず behavior を自分の語彙で codify する。
