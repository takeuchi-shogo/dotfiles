---
source: "https://zenn.dev/tokium_dev/articles/20260427_ai_tech_researcher"
date: 2026-06-04
status: planned
plan: docs/plans/active/2026-06-04-ai-tech-researcher-self-evolving-plan.md
---

## Source Summary

**主張**: 生成AIトレンドは週単位で変化するため、放置しても自動収集・レポート化し、かつ情報ソース自体が自己進化する仕組みが必要。核心は「レポートへの採用実績を評価指標に使い、情報ソース(キーワード/Webサイト/Slackチャンネル/Slackユーザーの4軸)をSQLiteで昇格降格管理」すること。

**手法**:
- 情報ソースの採用実績ベース自己進化(昇格/降格)
- 下流アウトプット採用を評価指標化
- 4軸独立進化(キーワード/Webサイト/Slackチャンネル/Slackユーザー)
- SKILL.md+shell 2層、claude -p 並列実行
- cron+GoogleDrive配信

**根拠**: 約3週間運用でデイリー15本/ウィークリー3本自動生成。「Mastra」が14日で自動昇格、「Copilot」が採用実績不足で段階的降格を実証。

**前提条件**: 社内Slackアクセス権を保持したまま育休に入れる環境。claude -p CLI/SQLite/cron。日本語AI技術情報(Zenn/Qiita等)が対象。

## Saturation Gate (Phase 1.5)

**判定: PASS (新分野)**。family taxonomy 4族にhitせず。最近接先行事例: Hermes personal analyst (2026-04-14) の auto-morning-briefing.sh (HN/arXiv/RSS統合)。N=1のため saturation 未到達。

## Gap Analysis (Pass 1: 存在チェック)

| # | 手法 | 判定 | 詳細 |
|---|------|------|------|
| 1 | 情報ソースの採用実績ベース自己進化(昇格降格) | Partial | learned-promotion-loop の「観測→候補→ledger→artifact」型が近い。新規SQLite不要、既存loopにsource_candidate入口追加程度 |
| 2 | 下流アウトプット採用を評価指標化 | Partial | learned-promotion-loopは「2スコープ再現」基準。「実際にレポート採用されたか」代理指標は未使用。主指標化は危険、ledgerにaccepted_in_artifact補助記録程度 |
| 6 | 4軸独立進化(Slackチャンネル/ユーザー監視) | N/A | 個人dotfilesに社内Slack監視は不要、プライバシー境界。キーワード+Webの2軸のみ採用 |

## Already Strengthening Analysis (Pass 2: 強化チェック)

| # | 既存の仕組み | 記事が示す弱点 | 強化案 | 判定 |
|---|---|---|---|---|
| 3 | auto-morning-briefing.sh(HN/arXiv/RSS固定、稼働中) | 情報源が手動env var固定で死角・陳腐化 | Experiment only/YAGNI注意。read-only集計に留める | Partial(強化対象、段階的) |
| 4 | dispatch+launch-worker.sh 2層オーケストレーション | (特になし) | 強化不要 | Already強化不要 |
| 5 | launchd 8本+crontab定期配信 | autoevolve-runner.shがcron未登録で一度も自動実行されていない(drift) | drift audit強化 | Partial(強化対象) |

## Phase 2.5 セカンドオピニオン要約

**Codex**: 採用本命は1件未満。やるなら「RSS候補のread-only集計」だけ。自動昇格降格は個人dotfilesではYAGNI。記事の核心は昇格だけでなく死んだ/ノイズ/重複/偏りソースの退役管理(在庫管理)。手法5のdrift audit過小評価(autoevolve-runner未登録=記事が避けたい「自動化したつもりで動いてない」問題)。

**Gemini**: 先行事例=Feedly Leo(採用学習)/Active Learning型検索。失敗事例=CTR採用実績はclickbait偏重。制約=エコーチェンバー(フィードバックバイアス)/コールドスタート/評価指標ゲーミング(LLMが要約しやすいソース偏好)/非定常性(降格ラグ)。代替手法=Multi-armed Bandit(UCB1/Thompson)で探索活用、LLM-as-judge多軸評価、Relevance Feedback、多様性強制(MMR)。

**両者一致の核心警告**: 評価指標ゲーミング + 探索欠如/コールドスタート。フル自己進化はYAGNI、read-only実験から。

## Integration Decisions

### Gap / Partial

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| 1 | 情報ソースの採用実績ベース自己進化 | 採用(Partial) | 既存loopにsource_candidateの観測入口を追加。自動昇格降格はYAGNI、read-only集計から |
| 2 | 下流採用補助指標 | 採用(補助のみ) | learned-promotion-loop本体への配線はせず干渉回避。思想として吸収、plan内で記録 |
| 6 | Slack2軸 | スキップ | プライバシー境界、個人dotfilesにN/A |

### Already 強化

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| 3 | morning-briefing RSS source候補集計 | 採用(Phase1実験) | read-only計測のみ。評価ゲーミング回避のため自動昇格は保留 |
| 4 | dispatch/launch-worker.sh | スキップ | 弱点なし |
| 5 | launchd/cron drift audit | 採用(Phase4) | autoevolve-runner未登録をmechanism化で検出する |

## Plan

### Phase 1: read-only MVP
- **Files**: `scripts/learner/source-collector.sh`(新規), `scripts/learner/auto-morning-briefing.sh`(既存)
- **Changes**: JSONL形式でRSS/Webソース候補を集計・記録。採用実績フィールドを追加(read-only)
- **Size**: M

### Phase 2: source ledger + 多軸選別
- **Files**: `scripts/learner/source-ledger.jsonl`(新規), `scripts/learner/source-ranker.sh`(新規)
- **Changes**: キーワード/Web 2軸でソース品質スコア記録。human-in-loop昇格降格(自動昇格はR1判定後)
- **Size**: M

### Phase 3: 半自動進化 (R1判定後)
- **Files**: source-ranker.sh, MAB実装
- **Changes**: UCB1/Thompson探索。MMRで多様性強制。Goodhartバイアス対策
- **Size**: L

### Phase 4: drift自己監視
- **Files**: `scripts/runtime/autoevolve-runner.sh`, `scripts/policy/drift-audit.sh`(新規)
- **Changes**: cron登録漏れを一般化検出するmechanism。autoevolve-runner未登録を修正
- **Size**: S

### 撤退条件
- **R1**: Phase1で2週間稼働しても採用改善なし → Phase2中止
- **R2**: ゲーミング検出(LLMが同じソースばかり採用) → 自動昇格停止
- **R3**: コールドスタート期に有用ソース全降格 → MAB探索率増加
- **R4**: morning-briefingとの軸重複 → 軸分離を強制設計で固定

## Validation-only Follow-up

記事framingが露出したdotfiles内drift:
- `scripts/runtime/autoevolve-runner.sh` がcron未登録で一度も自動実行されていない (learned-promotion-loop設計docで既出だが、本記事の「自動化したつもりで動いてない」framingで重要性が再確認)
- 対応方針: Phase 4 drift自己監視タスクで一般化検出する(個別修正ではなくmechanism化)

## 主要な教訓

1. **評価指標ゲーミング回避**: 採用実績を主指標にするとLLMが要約しやすいソースに偏る。補助指標に留め、多軸評価を並用
2. **自動化≠稼働**: cron未登録など「設定したつもりで動いてない」のdrift監視はmechanism化が有効
3. **在庫管理の視点**: 昇格だけでなく退役(ノイズ除去)こそ本質。ソースの「死」を検出する仕組みが先
4. **探索と活用のトレードオフ**: read-onlyで計測してからMAB段階移行。コールドスタートへの対策は設計段階で必要
