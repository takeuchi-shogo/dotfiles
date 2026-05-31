---
title: "My Agent Stack For Automating My Personal Life (Nicolas Bustamante) absorb 分析"
date: 2026-05-31
source:
  title: "My Agent Stack For Automating My Personal Life"
  author: Nicolas Bustamante
  type: blog
  fetched: pasted-text
family: personal-life-automation
status: implemented
adopted: 2
rejected: 6
---

# My Agent Stack For Automating My Personal Life — absorb 分析

## Source Summary

**主張**: モデルが十分賢くなった今、レバレッジは「既存ツール・データへの配線」から生まれる。
モデル選択（Claude Code → Codex/GPT-5.5 移行）は物語ではない。本質は tools + data connectors
+ skills + approval gates + taste の 5 要素を「自分が既に住んでいる世界」に配線すること。

**手法**:
- A) ツール表面の信頼性階層: API/CLI > local file > browser automation > screen automation
- B) Google Drive を agent-readable な source of truth に（Markdown/CSV、安定 file ID、JSON 返却）
- C) Skills = 操作マニュアルで taste を encode（inbox-zero 等の procedure が product）
- D) ミスを指示化するループ（tool 失敗→guardrail / 判断ミス→skill 更新 / 好み忘却→memory）
- E) approval gates = trust tiers（read / draft / send / destructive を分離、"approval gates are the product"）
- F) "What did I miss" 横断ライフトリアージ（first-pass=agent, 判断=human）
- G) モデルと API の間の抽象層を最小化（thin wrapper）
- H) personal connectors（gog / wacli / imsg / Telegram connector）

**前提条件**: personal life admin 自動化（email/WhatsApp/SMS/Calendar/Drive 横断）。Mac + Full Disk
Access 前提。本記事の対象 dotfiles は **コーディング用 harness** であり、personal admin ではない。

## Saturation Gate (Phase 1.5)

- Family: `personal-life-automation`（`docs/research/_index.md` に N=0 の新規候補として既登録）
- 判定: **PASS（新分野）**。同 family の過去 absorb なし。

## Pass 1 / Pass 2 判定テーブル（Phase 2.5 後の最終）

| # | 手法 | 判定 | 現状 / 根拠 |
|---|------|------|------------|
| A | ツール表面の信頼性ラダー | **Gap（採用）** | `cli-discovery.md` に発見順序（CLI→Skills→MCP）はあるが、信頼性の優先ラダー（file/CLI > MCP > browser > screen）は全 references に不在（grep 確認）。discovery 順とは別軸 |
| B | agent-readable source of truth | Already 強化不要 | 全面 Markdown、MEMORY.md サマリ+パス参照、Progressive Disclosure、agent-native-code-design.md。Notion→Drive 移行は N/A |
| C | Skills = 操作マニュアル | Already 強化不要 | 90+ skills + 「2 回説明したら書き下ろせ」(CLAUDE.md) + skill-writing-guide |
| D | ミスを指示化するループ | Already 強化不要 | core_principle「失敗→capability gap→durable artifact」+ friction-events loop + feedback_*.md + AutoEvolve + promote-patterns.py（2 回再発で昇格） |
| E | approval gates = trust tiers | **Gap（採用）** | deny rules（destructive 端）+ `/careful` + 「push はユーザー依頼時のみ」は散在するが、**read→draft→edit→commit→external→destructive の段階ラダーは未統一**。特に external side-effect（送信）ティアが独立明示されていない |
| F-principle | first-pass=agent, 判断=human | Already | 「Humans steer, agents execute」+ morning-briefing + daily-report + triage-router |
| F-life | 横断ライフトリアージ | N/A | personal connector 不在の coding harness では適用外 |
| G | 抽象層最小化 / thin wrapper | Already 強化不要 | wrapper-vs-raw-boundary.md + aci-tool-design.md + 「Meet agents at their abstraction level」 |
| H | personal connectors（gog/wacli/imsg） | N/A | コーディング harness に email/WhatsApp connector は不要 |

## Phase 2.5: Refine（Codex + Gemini 並列）

- **Codex（gpt-5.5, sandbox read-only）**: E と F を過小評価と指摘。「approval gate の read/draft/send/destructive
  は coding 版で `read > propose > edit > commit-push > external side-effect > destructive` の tier 表にできる」。
  優先採用は「A+E を 1 枚の判断表に統合」（"判断表で十分、実装追加不要"）。→ **採用**（cli-discovery.md に 2 軸統合表）。
- **Gemini（Google Search grounding）**: ツール実在性（gog/wacli/imsg は OpenClaw エコシステム、Open Interpreter が
  類似成功例、AutoGPT/BabyAGI が全自動失敗例）。記事未言及リスク（Full Disk Access によるプロンプトインジェクション
  全履歴流出、approval fatigue、Context Rot=Drive 古ファイル誤認）。「API/CLI > Browser > Screen はエージェント設計の
  鉄則（フォールバックラダー）」と A の業界標準性を裏付け。

## 採用 / 棄却の決定

- **採用 2 件（A + E、S 規模、統合 1 ファイル）**: `cli-discovery.md` に「2 つの直交ラダー」セクションを追加。
  - 軸 1（A）: ツール表面の信頼性ラダー — file/git/rg > 公式 CLI/API > MCP > browser snapshot > screenshot/screen
  - 軸 2（E）: 操作の信頼ティア — read > propose/draft > local write > commit > **external side-effect（送信）** > destructive
  - 2 軸は直交。`governance-levels.md` / `agency-safety-framework.md` への参照リンク付き。出典明記。
- **棄却 6 件**: B/C/D/F-principle/G（Already 強化不要、既存が記事より発達）/ F-life・H（N/A、coding harness に personal connector 適用外）

## メタ学習（重要 — Opus 自身の fabrication 罠）

1. **Opus がハロシネーションで Gap を Already に誤判定しかけた**: Phase 2.5 後、私は「`governance-levels.md` に
   L0-L4 action-trust 表（L3=External=push/PR/deploy）が既にある」と判断し E を「重複・取り下げ」としかけた。
   しかし実ファイルを読むと governance-levels.md は **AutoEvolve の自律性レベル**（Observe/Review/Auto-Merge/Trusted）
   であり、操作の trust tier とは無関係だった。grep ヒット（"governance-levels.md"）と自分の記憶から**存在しない表を
   想像で構築**していた。これは absorb skill が「Sonnet imagination」として警告する fabrication 罠を **Opus 自身が
   踏んだ事例**。教訓: 「Already だから取り下げ」の根拠も必ず実ファイルの該当行で確認する（grep ヒット名 ≠ 内容確認）。
2. **Codex の blind 批評が結果的に正しかった**: Codex は E を「過小評価（Gap）」と指摘。私は一度それを実ファイル誤読で
   覆そうとしたが、再検証で Codex が正しかった。Phase 2.5 の価値は「採用の根拠」ではなく「再検証のトリガー」。
3. **新分野 family でも採用は 2 件**: 成熟 harness に対し、記事のアーキテクチャ原則の大半は内面化済み。
   残ったのは「信頼性ラダー」と「操作信頼ティアの統一」という 2 つの未明文化軸のみ。

## Validation-only Follow-up

なし（既存 fact の drift は検出されず）。なお §メタ学習1 は外部 fact ではなく Opus の内部 fabrication 検出。

## 関連

- 採用先: `.config/claude/references/cli-discovery.md`（2 つの直交ラダー セクション）
- 参照リンク先: `.config/claude/references/governance-levels.md`（AutoEvolve 自律性）/ `agency-safety-framework.md`（Affordances）
- family 定義: `.config/claude/skills/absorb/references/topic-family-saturation.md`
</content>
