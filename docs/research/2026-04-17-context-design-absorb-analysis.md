---
source: "https://speakerdeck.com/ixbox/zu-zhi-de-naaihuo-yong-wozu-mu-zui-da-nohadoruha-kontekisutodezaindatuta"
title: "組織的なAI活用を阻む最大のハードルはコンテキストデザインだった"
author: "久保星哉 (株式会社アイスリーデザイン)"
date: 2026-04-17
status: integrated
plan: docs/plans/2026-04-17-context-design-absorb-plan.md
tags:
  - ingest
  - topic/context-design
  - topic/mcp
  - topic/skill-distribution
  - topic/governance
  - source/speakerdeck
---

# 組織的なAI活用を阻む最大のハードルはコンテキストデザインだった — 分析レポート

**日付**: 2026-04-17
**ソース**: 久保星哉 (株式会社アイスリーデザイン) — SpeakDeck 発表資料
**URL**: https://speakerdeck.com/ixbox/zu-zhi-de-naaihuo-yong-wozu-mu-zui-da-nohadoruha-kontekisutodezaindatuta
**分析対象**: 個人 Claude Code dotfiles ハーネス (/Users/takeuchishougo/dotfiles)
**フェーズ**: Extract → Analyze (Sonnet Explore) → Refine (Codex + Gemini 並列批評) → Triage → Plan

---

## Executive Summary

久保氏の主張は明快だ。「AIモデルの性能は既に十分。組織的AI活用の真の障壁はコンテキストデザインの欠如にある」。属人知が個人の頭の中や Slack のやりとりに閉じている限り、AI はその文脈を読み取れず、結果は属人スキルに依存し続ける。これを突破するために提唱されるのが 5 層構造 (Context Infrastructure → Creation & Editing → Skill Distribution → Action Governance → Execution) と、それを支える Phennec プラットフォーム (MCP 標準採用 + Git 連携 + 役割別パーソナライズ) だ。

オンボーディング 80% 削減（2週→2日）、リリースノート作成 92% 削減（3-4h→15min）、年間 4,360h 節約・ROI 24倍という定量実績は、定型業務に限定した前提付きではあるが、コンテキスト整備の効果を強く示している。

dotfiles 現状との照合では、12 項目中 5 項目が Gap/Partial であり、特に「Connector Inventory の分散（4箇所）」と「Telemetry 信号品質」が高インパクトの未対処問題として浮かび上がった。Codex は Telemetry 品質を全下流の前提と指摘し、Gemini は Hook 陳腐化リスクと組織手法の個人 overkill ラインを指摘した。取り込み決定は Gap/Partial 全 6 件 + Already 強化 4 件 = 計 10 タスク（L 規模）。優先度 P1 の基盤 2 件（Connector inventory + Telemetry 品質）を完了してから後続を進める依存構造にした。

---

## Phase 1: 記事要点 (Extract)

### 中核主張

AIモデル性能は既に十分。組織でのAI活用が進まない本質的な原因は、**コンテキストデザインの欠如**にある。チームメンバーの暗黙知・業務文脈・ドメイン知識が AI に渡っていないため、AI は「何を知っているべきか」を知らないまま動作する。この問題を解決するには、モデル選定ではなく、知識の構造化・配布・ガバナンスに投資すべきだ、というのが論旨の骨格。

### 5 層構造

| 層 | 名称 | 役割 |
|----|------|------|
| 1 | Context Infrastructure | 知識の収集・管理・バージョン制御基盤 (Git 等) |
| 2 | Creation & Editing | コンテキスト（ルール・スキル・知識）の作成・編集フロー |
| 3 | Skill Distribution | 役割・プロジェクト別のスキル配布・パーソナライズ |
| 4 | Action Governance | AI が実行できる操作の許可・拒否・監査 |
| 5 | Execution | 実際の AI 実行環境 (MCP 接続・ツール呼び出し) |

### Phennec プラットフォームの特徴

- **MCP 標準採用**: ツール接続を MCP に統一し、AI 側の接続ロジックを抽象化
- **Git 連携**: コンテキスト変更をバージョン管理し、ロールバック可能にする
- **役割別パーソナライズ**: エンジニア・PM・デザイナーで別々のスキルセットを配布

### 根拠・定量実績

- オンボーディング: 2週間 → 2日（80% 削減）
- リリースノート作成: 3-4h → 15min（92% 削減）
- 年間 4,360h 節約、約 2,180万円相当
- ROI 約 24倍

### 前提条件

- AIモデルの基礎性能は既に実用水準に達していること
- 組織にAI導入の意欲と投資余地があること
- Git 等の中央集権バージョン管理が利用可能なこと
- 定量実績は定型作業の計測値（非定型業務への拡張性は未検証）

---

## Phase 2: ギャップ分析

Phase 2.5（Codex + Gemini 並列批評）の反映を経た修正版。当初分析からの変更箇所は脚注に記した。

### Gap / Partial 項目

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | スキル配布・バージョン管理 | **Partial** | `skills-lock.json` は外部 skill のみを対象。`.agents/skills` の project-local skill には version contract なし。Codex 指摘: 「外部 skill のみ」という制約が明記されていない点が誤認リスクを生む |
| 4 | 監査ログ (Telemetry 品質) | **Partial (P1 昇格)** | `telemetry-coverage.md` が自己指摘済み: errors 過少記録、clean_success 過多、dead path。当初「Already」と判断したが Codex が覆した。「ある」≠「使える品質」。下流の T8(skill dashboard)・T10(tacit→rule trace)・定量効果測定の前提になるため P1 に格上げ |
| 5 | 予算管理 | **Partial** | `resource-bounds.md` の閾値警告 + `token-audit.py` は実装済。ただし金額コスト管理（API 費用・月次予算上限）は未実装。アクティブな強制機構もなし |
| 10 | MCP 非依存性 | **Partial** | `.mcp.json` + `mcp-audit.py` 実装済。真の問題は「文書化不足」ではなく **connector inventory 不足**: 移植性・代替手段・有効化状態の台帳が存在しない |
| 11 | **Connector drift 検査** (Codex 指摘・新規) | **Gap** | `.mcp.json` / `settings.json enabledMcpjsonServers` / `.codex/config.toml` / plugin enabled が 4 箇所に分散。差分検査なし。scite は設定済だが未有効化状態で放置されている |
| 12 | **Hook 陳腐化リスク** (Gemini 指摘・新規) | **Gap** | `<important if>` 条件タグはあるが、hook 自体の条件付き実行・自動スキップは未体系化。コードベースが変化しても hook が追従しない陳腐化パターンへの対処がない |

### Already 項目（強化候補）

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 2 | スキル作成 (Creation & Editing) | **Already (強化可能)** | `skill-creator` / `skill-audit` あり。使用率計測は弱い。どのスキルが実際に使われているか計測するダッシュボードがない |
| 3 | Action Governance | **Already (強化可能)** | `settings.json` allow/deny + 35 policy scripts で構築済み。ただし Codex 側 (`.codex/config.toml`) には同等の enforcement がなく、Codex 経由の操作が policy の盲点になりうる |
| 6 | Git 連携・symlink | **Already (強化不要)** | dotfiles 全体が symlink 管理済。コンテキスト変更はすべて Git 追跡下にある。これ以上の改善は費用対効果が低い |
| 7 | 役割・プロジェクト別パーソナライズ | **Already (強化可能・優先度高)** | `context-profiles.md` / `agent-execution-profiles.md` / `session-load.js` の task-aware profile が既に実装済。Codex 昇格: 個人利用こそ cwd-aware routing の効果が大きい。ただし cwd 自動切替で暗黙 chdir になるパターンは禁止（推奨出力のみ） |
| 8 | オンボーディング | **Already (強化可能)** | `developer-onboarding` + `init-project` あり。post-setup smoke-test がなく、初期設定の検証手段がない |
| 9 | 属人知資産化 | **Already (強化可能)** | AutoEvolve + `session-learner` あり。tacit→rule promotion の trace（「なぜそのルールが生まれたか」の履歴）が弱い |

---

## Phase 2.5: Refine — Codex + Gemini の貢献

### Codex の主要指摘

**見落とし の指摘**: 当初分析では Context Infrastructure 層（MCP connector surface）が実質的に分析外になっていた。`.mcp.json` と `.codex/config.toml` と `settings.json` で connector surface が 4 箇所に分散しているのに、差分検査が存在しない。これは発表資料の「Infrastructure 層」に直接対応する未対処 Gap であり、本分析で最も重要な新規発見になった（Gap #11）。

**過大評価 の是正**:
- #1 `skills-lock.json`: 外部 skill のみ対象という制約が既存分析に明記されておらず、project-local skill の version contract の欠如が見落とされていた
- #3 Action Governance: `settings.json` 側は整備済みだが、Codex 経由の操作には同等 enforcement がない盲点があった
- #4 Telemetry: `telemetry-coverage.md` の存在を「Already」と判断したのは誤り。自己指摘文書があること ≠ 品質が使えるレベルであること

**優先度批評**: Opus（当初分析）は定量効果測定を重視していたが、Codex は「Telemetry 信号品質が下流の全タスクの前提になる。T2 を先に直さなければ T8・T10・定量測定の結果が無意味になる」と指摘。順序を入れ替えた。

**cwd-aware routing への補足**: 個人利用では cwd が作業文脈を最もよく表す信号。ただし自動切替で暗黙 chdir になるパターンは避け、推奨出力のみにとどめるべきという制約付き賛成。

### Gemini の主要指摘

**類似事例・周辺知識**:
- **Cursor/Windsurf "Context Ops"**: `.cursorrules` 共有ライブラリの組織展開はメルカリ・LayerX 等が先行。dotfiles の approach はこれに近い
- **失敗モード類型**: Context Stuffing（詰め込みすぎ）、Skill 形骸化（作ったが使われない）、AI-Evals 運用負担（評価コストが高すぎる）。dotfiles の MEMORY 200 行制限・references/ 細分化はこれらへの適切な回答

**定量実績の読み方**: ROI 24倍・80-92% 削減は実観測値だが、定型作業に限定されている。非定型業務（設計議論・戦略立案）での効果は不明瞭。個人 dotfiles に適用する際は「再現性が高いのは定型フロー」という前提を維持すること。

**個人 overkill ラインの提示**:
- TELOS 3分割（Mission / Goals / Strategies）: 「概念としては有益だが個人に適用する粒度としては過剰の疑い」
- role-based governance: 組織向けの手法、個人には適用不要
- memory 3層スコープ: user / project / local の分離は個人でも明確な価値あり（採用継続を支持）

**Hook 陳腐化リスク (Gap #12)**:  `<important if>` タグは「Claude が読む条件」であり「hook が実行される条件」ではない。コードベース進化に伴い hook の前提が崩れたとき、自動スキップ・無効化の仕組みがなければ hook が false positive を出し続ける。

---

## Phase 3: 統合決定 (Triage)

### Gap / Partial — 全件採用

| # | 項目 | 優先度 | 採用理由 |
|---|------|--------|---------|
| 11 | Connector inventory + drift check | **P1** | 壊れると全作業波及。docs 1枚でも今すぐ価値がある |
| 4 | Telemetry 品質改善 | **P1** | 下流タスク全部の前提。T2 完了前に T8/T10 に進むことを gating で防ぐ |
| 10 | MCP 非依存性台帳 | **P3** | T1（connector inventory）完了後に連携して価値が上がる |
| 12 | Hook 条件付き実行体系化 | **P2** | Gemini 指摘。陳腐化リスクは時間経過で拡大するため早めに対処 |
| 5 | 予算管理（金額のみ） | **P3** | token 系は既存で十分。金額コスト管理だけ追加 |
| 1 | project-local skill version contract | **P3** | `skills-lock.json` 拡張で対応可能 |

### Already 強化 — 全件採用

| # | 項目 | 優先度 | 採用理由 |
|---|------|--------|---------|
| 7 | cwd-aware profile 明示化 | **P2** | Codex 昇格。個人環境こそ cwd が文脈を最もよく表す |
| 2 | スキル使用率 dashboard | **P4** | T2（Telemetry 品質）完了後の下流。既存部品あり |
| 8 | post-setup smoke-test | **P4** | 低コスト中価値。既存 init-project を拡張するだけ |
| 9 | tacit→rule promotion trace | **P4** | T2 完了後の下流。AutoEvolve の出力品質向上に直結 |

### スキップ

- **role-based governance**: 組織向け手法。個人 dotfiles では overkill（Gemini 指摘に同意）
- **TELOS 3分割の更なる細分化**: 既存の分割は維持するが、資料の組織向け構造を追加適用しない
- **Phennec プラットフォーム固有の実装**: SaaS 固有の部分（multi-tenant 管理等）は個人環境に不適

---

## Phase 4: 統合プラン

詳細は `docs/plans/2026-04-17-context-design-absorb-plan.md` に分離。以下は概要。

**規模**: L（10 タスク、4 フェーズ）
**推定工数**: 5-8 日（P1 のみでも 1-2 日で価値が出る）

### P1 基盤（T1, T2）— 他の全タスクの前提

| タスク | 対象 | 変更内容 |
|--------|------|---------|
| T1 | `docs/connector-inventory.md` (新規) | .mcp.json / settings.json / .codex/config.toml / plugin の 4 箇所を横断する Connector Inventory 作成。各 connector の: 名称・接続先・有効化状態・代替手段・移植性スコア・最終確認日 を記録。drift check スクリプト(`scripts/policy/connector-drift-check.sh`)で差分警告 |
| T2 | `scripts/lifecycle/telemetry-collector.*` (修正) | (a) errors を正確に記録: try/catch が握りつぶしているケースを洗い出し再計装。(b) clean_success の条件を厳格化: exit 0 ≠ success の場合を分離。(c) dead path 削除または到達可能状態に修正。(d) `scripts/learner/telemetry-quality-report.sh` 追加: 週次でシグナル品質を self-report |

### P2 個人効果（T3, T4）

| タスク | 対象 | 変更内容 |
|--------|------|---------|
| T3 | `.config/claude/references/context-profiles.md` (修正) | cwd-aware profile の明示化。現在の task-aware profile を cwd パターンと対応付け（例: `dotfiles/` = meta モード、`*/go/src/*` = backend モード）。推奨出力のみ、暗黙 chdir 禁止を明記 |
| T4 | `scripts/policy/hook-lifecycle.md` (新規) + 既存 hooks (修正) | Hook 条件付き実行の体系化。各 hook に: 適用条件・無効化条件・陳腐化トリガー を明記。`hook-health-check.sh` を追加し、条件を満たさない hook を警告 |

### P3 中コスト（T5, T6, T7）

| タスク | 対象 | 変更内容 |
|--------|------|---------|
| T5 | `docs/mcp-portability.md` (新規) | T1 connector inventory と連携した MCP 非依存性台帳。各接続の: 代替手段・OpenAPI 互換性・移植先候補 を記録 |
| T6 | `scripts/policy/budget-guard.py` (新規) | API 金額コスト管理スクリプト。月次予算上限閾値（configurable）を超えたら警告 + session 新規開始を抑制 |
| T7 | `skills-lock.json` (修正) | project-local skill のバージョン契約を追加。`.agents/skills/` の各エントリに: 作成日・最終更新・依存 references の hash を記録 |

### P4 下流（T8, T9, T10）— T2 完了後に着手

| タスク | 対象 | 変更内容 |
|--------|------|---------|
| T8 | `scripts/learner/skill-usage-dashboard.sh` (新規) | Telemetry データを使ったスキル使用率レポート。既存の `token-audit.py` 出力と合わせて週次 summary |
| T9 | `scripts/lifecycle/post-setup-smoke-test.sh` (新規) | `init-project` 完了後に実行する smoke-test。symlink 確認・必須 env 変数確認・MCP 接続疎通を自動検証 |
| T10 | `scripts/learner/tacit-rule-trace.md` フォーマット + `session-learner` 修正 | tacit→rule promotion の trace 記録。「なぜそのルールが生まれたか」（元となったセッションログ・friction-event）を rule ファイルにコメントとして埋め込む仕組み |

### 依存関係

```
T2 (Telemetry) → T8 (skill dashboard)
T2 (Telemetry) → T10 (tacit→rule trace)
T1 (Connector inventory) → T5 (MCP 非依存性台帳)
T4 (Hook lifecycle) — 独立
T3, T6, T7, T9 — 独立
```

P1 完了を gating として P2 以降に進む。T8/T10 は T2 完了まで着手しない。

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| 10タスク一気に取り込んで Context Stuffing | 中 | フェーズ分割。P1 完了確認してから P2 着手。各フェーズは独立デプロイ可能な単位に設計 |
| 組織向け手法を個人 dotfiles に過剰適用 | 中 | TELOS 3分割・role-based governance は採用しない（Gemini 指摘反映）。「個人 overkill」判定基準: 管理コスト > 節約時間 なら採用しない |
| T2 telemetry 品質を直さず T8/T10 に進む | 高 | 依存関係を明記し P1 を gating。T8/T10 の PR では T2 完了を前提条件チェックに含める |
| cwd 自動切替で暗黙 chdir になる | 中 | T3 に「推奨出力のみ、暗黙 chdir 禁止」を明記（Codex 指摘）。実装時に chdir を含む実装は block |
| Connector inventory が陳腐化する | 低 | T1 で `connector-drift-check.sh` を pre-commit hook に組み込み、.mcp.json 変更時に inventory 更新を強制 |
| Hook 体系化が過剰官僚化する | 低 | T4 は「条件明記」と「health-check」のみ。hook の動作を変えるのではなく可視化にとどめる |
| ROI 24倍の前提（定型作業限定）を忘れる | 低 | 非定型業務での効果測定は T8 の scope 外とする。測定対象を定型フローに限定することを dashboard の仕様に明記 |

---

## 参考文献・関連ファイル

### 関連既存ファイル

- `.config/claude/references/context-profiles.md` — task-aware profile 実装
- `.config/claude/references/agent-execution-profiles.md` — execution profile 定義
- `scripts/lifecycle/session-load.js` — profile ロード処理
- `scripts/policy/output-offload.py` — output 隔離ポリシー
- `scripts/learner/telemetry-collector.*` — telemetry 計装
- `docs/agent-harness-contract.md` — hook 契約書
- `.mcp.json` — MCP connector 定義
- `skills-lock.json` — 外部 skill version lock

### 比較事例（Gemini 提供）

- Cursor/Windsurf "Context Ops": `.cursorrules` 共有ライブラリ（メルカリ・LayerX 等）
- Letta/MemGPT 階層型メモリ — 参照アーキテクチャとして有用
- Voyager skill library — スキル積み上げパターン

### _index.md への追記候補

```markdown
| 2026-04-17 | 組織的なAI活用を阻む最大のハードルはコンテキストデザインだった | https://speakerdeck.com/ixbox/zu-zhi-de-naaihuo-yong-wozu-mu-zui-da-nohadoruha-kontekisutodezaindatuta | integrated | context-design, mcp, skill-distribution, governance, connector-inventory, telemetry | T1-T10: connector-inventory, telemetry 品質, cwd-aware profile, hook lifecycle, MCP 台帳, 予算管理, skill lock, skill dashboard, smoke-test, tacit-trace に統合予定 |
```
