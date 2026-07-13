---
source: "努力の天才「落合陽一」がやってるAI活用術 (著者不明のWeb記事、テキスト貼り付け、URL なし)"
date: 2026-07-14
status: analyzed
family: none (新分野: celebrity-ai-workflow)
---

## Source Summary

**主張**: AI時代の努力は反復削減ではなく「試行・仮説・検証の回転数を上げる構造」作りである。成果の質は「問いの質×試行回数×検証力×実装速度×現実フィードバック」で決まる。

**手法** (14個、Phase 2 では細分化して16項目として判定):
- 複数AI並列運用と差分読み
- 音声素材回収と自動分類 (事実/解釈/仮説/矛盾)
- 工程分割+人間関門
- ディープリサーチの調査地図化 (証拠台帳: 主張/出典/公開日/対象期間/一次二次/反対証拠/確信度)
- プロンプト=仕様書 (停止条件・ツール権限含む)
- 却下理由の生成条件化
- 仕様矛盾の発見力
- 反証監査 (別AIに壊させる、重大度4段階)
- 繰り返す不便の道具化 (vibe-local/co-vibe)
- 対話的要件定義 (AI=曖昧さ発見装置)
- ログ化・観察可能性
- 努力の場所の転換
- 現実フィードバック接続
- 好奇心の余白

**根拠**: 記事本文の記述のみ (実証データ・出典の明示なし)。

**前提条件**: 個人の知的生産・研究/探索寄りのワークフロー。当リポジトリのような「変更安全性最適化を目的とする operational harness」とは前提が異なる。

## Gap Analysis (Pass 1: 存在チェック)

Saturation Gate 判定: **PASS (新分野扱い)**。既存 taxonomy 4族 (obsidian-second-brain / skill-graphs / harness-engineering / claude-code-tips) はすべてキーワード閾値未達。「著名人のAIワークフロー」ジャンルは今回が初めて。multi-agent-orchestration 系 (informal N=14) との手法重複は Pass 2 で個別照合した。

## Already Strengthening Analysis (Pass 2: 強化チェック)

Pass 1 = Sonnet Explore, Pass 2 = メイン判定。

| # | 手法 | 判定 | 根拠 |
|---|------|------|------|
| 1 | 対話型要件定義 | Already (強化不要) | grill-me / interviewing-issues / grill-interview でカバー済み |
| 2 | 音声/未整理キャプチャ→分類 | Partial → 採用 | `/note` は Inbox 保存のみで、分類軸 (事実/解釈/仮説/アイデア/矛盾) が不在 |
| 3 | 複数AI並列 triangulation | Already (強化不要) | `/debate` + hub-and-spoke conductor。同一質問設計は合意率算出のための意図的設計 (Codex: same-question は bias 検出で role-split より強い場面あり) |
| 4 | 工程分割+人間関門 | Already (強化不要) | S/M/L workflow + Codex Spec/Plan/Review Gate |
| 5 | 調査地図 (証拠台帳) | Already (強化可能) → 採用 | deep-research/research に Confidence 欄はあるが、公開日 vs データ対象期間・一次/二次区別・反対証拠欄・数値相違理由推定が template に不在 (grep で確認済み) |
| 6 | プロンプト=仕様書 | Already (強化不要) | prompt-as-prd-template に Exit Criteria あり。停止条件は workflow gate、ツール権限は settings.json/sandbox が harness レベルで担保 (Codex: sandbox=権限境界 / spec stop condition=判断境界、役割は違うが必須 field 化は過剰) |
| 7 | 却下理由の生成条件化 | Already (強化不要) | contextual commits の rejected()/learned() + promote-learnings。即時禁止リスト直結は human-in-loop cadence を壊すため不採用 (Codex 追認) |
| 8 | モデル振り分け・自作ツール | Already (強化不要) | model-routing.md + cmux + launch-worker.sh |
| 9 | 観察可能性ログ | Already (強化不要) | session observer は消費者ゼロで 2026-06-05 退役済み。記事は新規消費者を提示せず、再導入は退役判断と矛盾する |
| 10 | 作成者/評価者分離 | Already (強化不要) | PR #157 eval judge 独立性 + codex-reviewer/code-reviewer 並列 |
| 11 | 反証監査 | Already (強化不要) | challenge + pre-mortem + security-reviewer。重大度4段階は既存 severity 慣行でカバー |
| 12 | 不便の道具化 | Already (経路変更済) | promote-learnings 経由の learned 昇格。Validation-only Follow-up 参照 |
| 13 | 反復探索+修正理由記録 | Already (強化不要) | challenge / review-loop / contextual commits |
| 14 | 好奇心の余白 | Gap (弱) → 見送り | timekeeper に不在。Codex「作業管理と生活習慣が混ざる」→ harness 化せず。ユーザーも見送り選択 |
| 15 | 手作業経験=検査装置 | N/A (Reference Only) | 学習哲学。/quiz・/teachback・deep-read が学習面をカバー |
| 16 | 環境・空間・身体接続 | Already (薄いが十分) | Ghostty + cmux。通知遮断等は OS レベルの個人 practice で harness 外 |

## Integration Decisions

### Gap / Partial

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| 2 | 音声/未整理キャプチャ→分類 (`/note`) | 採用 (T2) | 分類のみ・自動昇格なしの S 規模スコープに固定 |
| 14 | 好奇心の余白 | スキップ | harness gap として弱い。reference/playbook 扱いが適切、ユーザーも見送り選択 |

### Already 強化

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| 5 | 調査地図 (証拠台帳) | 採用 (T1) | research/deep-research の template に一次二次・反対証拠・数値相違理由推定まで拡張して具体フィールド不足を解消 |

## Phase 2.5 Refine

- Gemini 経路は degraded (IneligibleTierError、individuals sunset — 2026-07-05 再確認済み)。Codex 単独批評で実施し、モデルファミリ多様性は縮退した。
- Codex 批評 (codex exec read-only, gpt-5.5 high) の主な指摘と反映:
  1. ENHANCE-A (証拠台帳) が狭い → 「公開日/対象期間」だけでなく一次二次・反対証拠・相違理由まで拡張して採用 (反映済み)
  2. curiosity slack は harness gap として弱く、reference/playbook 扱いが適切 → 降格、ユーザー見送り
  3. `/note` 分類は分類のみなら S、検索・昇格まで含めると M → スコープを「分類のみ・自動昇格なし」の S に固定
  4. role contract 明文化提案 → cmux-ecosystem.md:110-133 で役割割当+撤退条件つき統合が明文化済みと確認、不採用
  5. same-question debate / rejected-tags / observer 退役 / spec 欄不採用はすべて Codex 追認
  6. premise mismatch: 記事は個人の知的生産・探索寄り、当 harness は変更安全性最適化の operational system。全部 harness 化すると重くなるという全体基調は妥当

## Plan

### Task 1: research 証拠台帳フィールド拡張 (T1)
- **Files**: `.config/claude/skills/research/templates/research-report-template.md`, `.config/claude/skills/research/templates/subtask-prompt.md`
- **Changes**: Source type (Primary/Secondary)、Published vs Data period、Counter-evidence のフィールドと、数値相違時の理由推定ルールを追記
- **Size**: S

### Task 2: /note 保存前分類 schema (T2)
- **Files**: `.config/claude/skills/note/SKILL.md`
- **Changes**: 保存前分類手順 (事実/解釈/未検証の仮説/アイデア/矛盾・違和感) を追加。空カテゴリは省略、短文はそのまま保存、自動昇格なし
- **Size**: S

## Phase 4 実装状況

T1・T2 とも同一セッションで実装済み。

## Validation-only Follow-up

| 対象 | drift 内容 | 訂正方針 |
|------|-----------|---------|
| `references/improve-policy.md` Friction → Eval Loop (L153+, R3) | 記事の「繰り返す不便の道具化」framing で露出: friction-events.jsonl の producer が停止 (errors.jsonl 16日 / friction 25日 停止と L11 に自記)、R3 の B1 接続も未了。仕組みは文書化済みだが非稼働 | ユーザー判断「レポート記録のみ」。対処 (producer 復旧 or セクション retire) は別途判断。採用件数には数えない |

## 教訓

- 著名人ワークフロー記事でも、成熟した harness では 16 手法中 14 が Already/N/A。採用は「テンプレの具体フィールド不足」という末端の粒度でのみ発生した。
- Gemini sunset 後の Phase 2.5 は Codex 単独判定が常態化し、モデルファミリ多様性による bias mitigation の設計前提が弱まっている (absorb skill 側の将来課題)。
