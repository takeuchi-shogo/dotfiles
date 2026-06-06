---
source: "Claude Code で自己改善ループを作った話 (sonicgarden, hiroro-work)"
url: "https://zenn.dev/sonicgarden/articles/claude-code-self-improving-loop"
date: 2026-06-05
status: implemented
family: self-evolving-self-improving-agents
adopted: 2
---

## Source Summary

**主張**: Claude Code スキル (`dev-workflow`) の改善サイクルを「会話履歴からの自己ふりかえり → GitHub Issues 起票 → Routines による無人 triage → PR 作成」の 3 段で自動化できる。人間のレビュー・マージを残しつつ、ふりかえりから PR 出しまでを無人で回し、スキルが継続的に自己改善する。

**手法**:
1. 会話 JSONL からの自己ふりかえり (発見ステージ) — 最新 session JSONL をサブエージェントに渡し「うまくいかなかった signal」(ユーザー修正指示/繰り返し指示/進まないループ/SKILL.md root-cause 名指し) を抽出
2. GitHub Issues への課題自動起票 (1 Issue = Finding 1〜4 件)
3. dev-workflow-triage スキル (無人運転前提) — 対話用 dev-workflow と分離し、Issue を accept/reject 判定 → SKILL.md 修正 → PR 作成
4. 3 段品質ゲート (verify-diff / skill-review / publicity-review) — 内側ループ + 外側収束ループ
5. Claude Code Routines による 1 日 1 回の無人実行 (human-in-the-loop でマージ)
6. Routines 環境でのハマりポイント対策 5 点 (停止回避 liveness 条件)

**根拠**: 著者 1 人・13 日試験運用で auto-triage コミット 40 件以上が PR 経由で main に。自己ふりかえり Issue 21 起票・21 close・0 open。明らかな改悪なし。

**前提条件**: SKILL.md ベースのローカルスキル、session JSONL 環境、GitHub Issues、Routines (Claude Code on the Web) が利用可能であること。

## Saturation Gate (Phase 1.5)

- **Family**: self-evolving/self-improving agents, **N≥10** (registered taxonomy には未登録だが MEMORY.md が N≥10 と認識)。本記事は「**どう自己進化するか (実装手法)**」側で過去 9 件と同カテゴリ
- **採用率**: 高い (SkillOpt 採用4 / RSI 採用3 / ai-tech-researcher L plan 採用 / Environment-Driven RL plan / Universal Verifier plan) → SATURATED にならず **PASS (warning)**。連続 reject trend でもない
- **判定**: PASS (warning, 重複領域)。フル workflow 実行
- **重要文脈**: 昨日 (2026-06-05) の RSI governance absorb が「過去 9 件は全て execution の自己改善で重投資済、未踏は判断の計測とメタ安全層」と結論。本記事は execution 側なので大半が既存

## Gap Analysis (Phase 2 + 2.5, per-method 照合台帳)

| # | 手法 | Pass1 | Phase 2.5 修正後 | 根拠 / matched_prior |
|---|------|-------|------------------|----------------------|
| 1 | 会話 JSONL 自己ふりかえり | Partial | **N/A** | session-observer + stagnation-detector(hook) + meta-analyzer 存在。Codex: 生 JSONL 質的抽出の full pipeline 化は不要、`patterns.jsonl` 主軸 + spot audit で十分 |
| 2 | GitHub Issues 自動起票 | Partial→Gap | **N/A (媒体差)** | Codex: Gap ではなく媒体差。`patterns.jsonl`/ledger が backlog として機能するなら GitHub 化は不要 |
| 3 | 無人 triage スキル | Partial (retire残骸) | **不採用** | autoevolve-core Improve phase が相当だが legacy/retire。Codex/Gemini 一致: 記事の簡素版でも accept/reject + SKILL.md 修正の無人化は `/improve` の二の舞 (false-positive)。autoevolve-core は復活させない |
| 4 | 3 段品質ゲート | Partial | **publicity-review のみ Gap → 採用** | verify-diff=empirical-prompt-tuning / skill-review=adversarial-gate で既存。publicity-review (公開リポ leak gate) のみ未組込。Codex: public dotfiles で secret 以外に個人パス/hostname/内部名 leak が現実的 |
| 5 | Routines 定期実行 | Already | **Already (強化不要)** | launchd daily-health-check 稼働 / managed-agents-scheduling.md / scheduling-decision-table.md。同等以上 |
| 6 | Routines ハマり対策5点 | Already強化可能 | **採用 (doc 教訓)** | Codex: Already ではなく小さく強化すべき liveness 条件。daily-health-check とは別責務 (サブスキル跨ぎ Routine で効く) |

## Phase 2.5: Codex + Gemini

- **Codex 結論**: Opus 判定は大筋正しい。記事の真の差分は「Issue/PR という媒体」ではなく「失敗 signal を独立 backlog 化し、無人修正を publicity-review 付きで PR 手前で止める収束ループ」。個人 harness に欠けるのは leak gate のみ。**最終推奨採用: 1 件 (publicity-review)**。GitHub Issue 自動起票/無人 triage/autoevolve-core 復活は不採用。Routines 5点は docs 教訓扱い
- **Gemini grounding (裏取り)**: ① hiroro-work/claude-plugins 公開実在、破壊的修正リスク文書化 ② 自己修正の既知リスク = 報酬ハッキング/破滅的忘却/セマンティックドリフト/非収束ループ (2025-26 研究) → `/improve` retire の正しさを裏付け ③ Routines 実在 (GA Preview、Schedule/API/GitHub Events トリガー。回数上限の具体値は要検証 = Gemini 生成疑い) ④ 判断系最適化の Goodhart/欺瞞的アライメント/透明性喪失が SkillOpt 結論と独立一致

## Integration Decisions

| 項目 | 判定 | 規模 |
|------|------|------|
| publicity-review gate (公開差分への credential leak 検査) | **採用** | S |
| Routines liveness 対策5点 (routine-prompt-rubric.md 追記) | **採用** | S |
| 会話 JSONL full pipeline / Issue 自動起票 / 無人 triage 復活 / autoevolve-core 復活 | **不採用** | — |
| Routines 定期実行 | N/A (Already) | — |

## 実装 (Phase 4/5, インライン完了)

1. **`scripts/security/publicity-scan.py`** 新設 — staged added-lines の credential leak を block する pre-commit gate。既存 `scan-jsonl-secrets.py` の `PATTERNS` を importlib で DRY 再利用 (`sys.modules` 登録で dataclass resolution 対応)。
   - **スコープ翻訳**: 記事の publicity-review は「絶対パス/hostname/credential/ユーザー識別子」を見るが、この dotfiles は public でも `/Users/takeuchishougo/` と username が全体に意図的に埋め込み済 → hard block は constant-fail NO-OP になる。よって **credential のみ block**、絶対パス/username は accepted-in-repo として明示除外 (docstring に記録)
   - **severity 設計 (Codex Review Gate で修正)**: 当初 high のみ block・medium warning だったが、Codex 指摘「medium (sk-*/Bearer/api_key=) は本物の credential を含み warning-only は leak を通す」を受け **high+medium を block** に昇格。low (password_assignment = doc 例の FP 磁石) のみ warning
   - **added-lines only**: legacy 内容は再 scan しない (check-new-todo と同方式) ため導入で既存ファイルが retroactive fail しない
2. **`lefthook.yml`** pre-commit に `publicity-review` コマンド配線。skip: `LEFTHOOK_EXCLUDE=publicity-review git commit`
3. **`routine-prompt-rubric.md`** に「無人実行の liveness 対策」セクション + Pre-flight Checklist 1 項目追記

**検証**: ruff clean / clean stage exit 0 / 偽 AWS key で exit 1 / medium sk-token で exit 1 (Codex 修正後) / low password で warning のみ exit 0 / 絶対パス+username で exit 0 (block しない) / validate-configs exit 0 / **lefthook 経由で実発火確認** (`🥊 publicity-review` が AWS key を block)。

**Codex Review Gate 結果**: (A) medium → block 昇格で対応済。(B) hook ordering (stage_fixed formatter 後の index 読取保証) は既存 check-new-todo と同方式の構造的制約で新規衝突ではない → 据え置き。(C) **既知の制限**: 共有 PATTERNS は legacy GitHub PAT (`ghp_`) のみ、fine-grained token (`github_pat_`/`gho_`/`ghu_`/`ghs_`) 未カバー。`scan-jsonl-secrets.py` (他 caller と共有) 側で別途強化すべき follow-up (本変更のスコープ外、docstring に記録)。

## 残す洞察

- **記事の価値は手法そのものより「シンプルに動く統合」という教訓**。あなたの harness は記事のループ全体を既に持つ (一部は意図的に retire)。記事を「全部導入」するのは昨日の RSI absorb 結論 (execution 自己改善は重投資済) と逆行する。新規に足す価値があったのは欠けていた 1 ピース (publicity-review) のみ
- **`/improve` retire の正しさが外部から二重に裏付けられた**: Codex (無人判断自動化は失敗モード同じ) + Gemini grounding (報酬ハッキング/Goodhart は 2025-26 研究で確立)。記事の簡素版でも無人 accept/reject を戻さない判断は妥当
- **enterprise/別リポ → 個人 public repo の absorb ではスコープ翻訳が必須**: publicity-review を素朴に hard block すると既存の username/path で constant-fail。「原則 (leak を止める) は採用、適用範囲 (何を leak とみなすか) はリポ実態に翻訳」した (zero-trust absorb の教訓と同型)

## Follow-up: self-improving loop 本体の実装と撤退 (2026-06-06)

初回 absorb (2026-06-05) は publicity-review + Routines liveness のみ採用したが、ユーザーが「一部でなく全部高品質に、完全無人で (記事額面通り)」と再要求。記事の self-improving loop 本体 (発見→backlog→無人triage→PR) の実装を試み、段階導入で検証した結果、**Wave3 (learned → 無人 PR 化) は構造的に YAGNI** と判明して撤退した。

### 実装したもの (master 統合済み)
- **Wave1 `a3e8c8e`**: `session_events.py` に `from __future__ import annotations` 追加。PEP604 union (`str | None`) が実行時評価でクラッシュし、自己改善ループの**発見ステージ (learned 流入) が死んでいた根因**を修正。これは Wave3 の YAGNI 判定とは独立に価値があり**残す**
- **Wave2 `7a1c556`/`78cc902`**: `auto-triage` dry-run skill + cron runner。learned 候補を mechanical/advisory/reject/defer に無人分類しレポートのみ出す (artifact 編集なし)

### calibration の決定的 finding: mechanical 0/139
全 139 件 learned を分類 → **mechanical 0 / advisory 129 / reject 5 / defer 5**。borderline (tournament-mode リンク切れ / `/ultra-review` typo / agent-count drift) も精査したが全て「判断が要る」で advisory。

**構造的洞察**: learned ストアは本質的に「経験から得た判断材料 (advisory)」で、機械照合可能な mechanical を**原理的に含まない**。記事の「learned → 無人 PR」ループは、learned の性質上そもそも燃料が出ない。これは2週間 calibration を待たず初日に確定した。

### 撤退と最終形
- **撤退**: auto-triage-runner の cron 日次実行を撤去 (毎日同じ上位 N を見る無駄 + Wave3 YAGNI)。calibration リマインダーも不要として破棄
- **残す**: Wave1 修正 (learned 流入回復) + auto-triage skill (手動再 calibration 用)
- **本来の価値**: learned の advisory 129 件は**対話型 `/promote-learnings` で昇格**するのが筋。これが死んでいたループの本体で、Wave1 で燃料が回復した
- **無人化したいなら別設計**: 入力源を learned ではなく lint 差分 / 静的解析 / リンクチェッカー出力に変える (本タスクの範囲外)

### 段階導入が効いた教訓
「完全無人で全部」を額面通り実装せず dry-run 段階を挟んだことで、**無人 PR 化の本体を作る前に「燃料が構造的にゼロ」と実装コストほぼゼロで判明**した。Codex Spec/Plan Gate の「完全自動は誤爆」+ design doc の「完全自動は誤爆」が、実データ (mechanical 0) で裏付けられた。記事の N=1 (13日1人) を鵜呑みにしない判断が正しかった。

### dry-run skill の設計上の穴 (記録)
auto-triage は dry-run で ledger に書かないため、cron 日次だと毎日同じ importance 上位 N 件を分類する (calibration にならない)。期間 calibration は無意味で、全件1回分類が正しかった。この穴は Codex Gate も突かなかった (dry-run の繰り返し挙動)。
