---
date: 2026-07-11
source: https://zenn.dev/layerx/articles/797bb5b8935bf6
family: task-management (新分野、初 absorb)
status: analyzed
adopted: 3
---

## Source Summary

- 記事: LayerX uphy「判断は人間、更新はエージェント、計算はスクリプト」(Zenn, 2026-07)
- 主張: タスク管理はツールでなく責務分担から設計する。判断は人間（文脈の書き切れなさはモデル進化で解決しない）、更新は単一 writer サブエージェント、計算は決定論スクリプト、実行契機は PostToolUse hook
- 手法10個: (1)1タスク=1ファイル frontmatter SSoT (2)ビューは全て派生・手編集禁止 (3)書き換えは task-manager 単一 writer (不変条件10個/約240行仕様/判断させない) (4)計算は決定論 Python (5)実行契機は PostToolUse hook (6)ローカル Markdown が成立条件 (7)チーム同期 opt-in + サブツリー根フラグ除外 (8)owner のみ書き戻し・close は Done 遷移 (9)4モード運用+「次のタスクやって」EM視点ループ (10)能力不足補完の仕組みは負債・精度/コスト保証の仕組みは永続
- 根拠: Markdown ライト運用5年→整合保守で崩壊、LLM丸投げ→文脈不足で崩壊。新方式23日でタスク100件(closed49/todo47/in_progress4)、ビュー常時一致
- fetch_metadata: route=defuddle, 21938 bytes, 全文視認

## Saturation Gate (Phase 1.5)

- family 判定: 該当なし → PASS 新分野。obsidian-second-brain は hit 2/3 (`obsidian`,`vault`)、harness-engineering は hit 1/3 (`hook`) で閾値未達。task-management family として初回（taxonomy 追加は3件累積まで保留）

## Gap Analysis (Phase 2 → 2.5 修正後)

| # | 手法 | 最終判定 | 根拠 |
|---|------|---------|------|
| 1 | 1タスク=1ファイル SSoT | Foundational Gap | `type: task` スキーマは templates/obsidian-vault/Dashboard.md に定義済だがキャプチャ導線なし。スキーマ存在≠SSoT (Codex 指摘) |
| 2 | 派生ビュー | Weak Partial | Dataview live query (Today/Carryover/Open Loops) は「手編集しない派生ビュー」を満たす。ガント/依存図なし。生成責任境界が薄い |
| 3 | 単一 writer agent | Conditional Gap (今は YAGNI) | 個人・低 volume。「入口を1 skill に寄せる+validator」で代替 (Codex 指摘で Gap から降格) |
| 4 | 決定論スクリプト | 原則 Already / タスクドメイン未移植 | determinism_boundary.md 内在化済。ただし PLANS.md の厳密さ (validator/自動クローズ) が個人タスク側に無い |
| 5 | PostToolUse hook 再生成 | Dependent Gap | SSoT とスクリプトが先。hook は仕上げの強制層 (Codex: 最初に作ると空回り) |
| 6 | ローカル Markdown | Already 強化不要 | Vault + dotfiles 全て local markdown + git |
| 7 | チーム同期 opt-in | N/A | Notion/チームボード不存在 (個人完結) |
| 8 | 書き戻し安全規則 | Partial 適用 (N/A から昇格) | Notion 不要でも「close は削除でなく状態遷移」「自動処理が触れる範囲」規約は必要 (Codex 指摘) |
| 9 | 4モード運用 | Critical Gap (最優先) | daily note が 07-Daily (timekeeper/sync-daily-report) と 00-Inbox (auto-morning-briefing.sh:22) に分裂 = 記事第1期崩壊「真実の二重化」と同型 |
| 10 | 負債/永続の補助線 | Already 強化不要 | Build to Delete 原則と同型 |

## Phase 2.5 Refine

- Codex (gpt-5.5, codex exec read-only, medium effort): 判定修正 7 件 (上表反映)。核心指摘 =「記事の本質は 1タスク=1ファイルではなく、write path 単一化 + derived state 非権威化 + failure mode 設計の合成。取り込む中心は writer agent ではなく真実の置き場所を1つにすること」。優先順 = 分裂解消→SSoT→validator→(条件付き)writer agent→hook
- Gemini: IneligibleTierError (individuals sunset) により恒久 degraded、Codex 単独で実施
- 初回 codex exec (xhigh) は無出力 → medium effort 再試行で成功。cmux 不在で launch-worker.sh は exit 1

## Adopted (3件, T1+T2+T3, M規模)

- T1 (S): daily note 分裂解消 — scripts/runtime/auto-morning-briefing.sh:22 の DAILY_NOTE_DIR を 00-Inbox→07-Daily。00-Inbox は capture 専用と規約明記。edge case: timekeeper テンプレとの prepend 衝突を実装時検証
- T2 (M): タスク SSoT 最小構築 — timekeeper SKILL.md Plan フェーズに「タスクは task file (type/status/due/priority) へのリンクで記録、実体複製禁止、無ければ 01-Projects/ 配下に作成」ステップ追加。close は status: complete 遷移。depends_on/estimate は入れない
- T3 (S): scripts/runtime/task-lint.py 新規 (frontmatter スキーマ検証/タイトル重複/daily note との二重管理検出、レポートは 00-Inbox/ 出力) + weekly-review SKILL.md に実行ステップ追記

## Integration Plan

上記 T1〜T3 を Adopted セクションの内容通りに実施する。優先順は Codex 指摘に従い「分裂解消(T1)→SSoT(T2)→validator(T3)」。writer agent と hook は Deferred へ。

## Deferred (導入条件つき)

| 項目 | 導入条件 |
|------|---------|
| task-manager 単一 writer agent | 複数 skill がタスクを書く / 100件規模 / depends_on 運用開始 |
| PostToolUse hook ビュー再生成 | 派生ビュー生成 script が存在してから |
| ガント・依存関係図 | depends_on 運用開始後 |
| Dataview→Bases 移行 | 独立タスク |

## Rejected

- チーム同期 (手法7,8 の Notion 部分): チームボード不存在
- tasks/ 専用フォルダ新設: 既存 PARA + type:task frontmatter 方式で充足

## 教訓

- 記事の framing が既存バグを露出した実例: daily note 保存先分裂 (07-Daily vs 00-Inbox) は記事の「真実の二重化」レンズで Critical と判明
- 開発ハーネスに内在化済みの原則 (決定論境界) が、隣接ドメイン (個人タスク) に未移植というパターン — 「原則 Already ≠ 全ドメイン適用済」

## Review Gate 結果と既知の制約 (2026-07-11 実装)

T1+T2+T3 を worktree で実装し Codex Review Gate を通過 (codex-reviewer は Codex CLI 障害で手動分析にデグレード、Gemini は sunset で 2-way)。edge-case-hunter と codex が独立に指摘した項目を修正:

- **task-lint.py の確定バグ修正**: (a) `UnicodeDecodeError` 未捕捉クラッシュ → `except (OSError, UnicodeDecodeError)` (b) vault パス不在で偽 clean → `is_dir()` チェックで exit 2 (Fail Fast) (c) BOM 付きノートが無警告でスキャン漏れ → BOM strip (d) 暦として無効な日付 (2026-13-40) が通過 → `date.fromisoformat` 検証 (e) double-management の substring 誤検知 → 4文字未満 title をガード + exit code 分離 (schema/duplicate=violation exit 1、double-management=warning exit 0)。self-test に回帰 assert 6件追加、exit code 3分岐を実挙動で検証済

### 既知の制約 (defer、実運用で顕在化したら対処)

| 制約 | 内容 | upgrade path |
|------|------|------------|
| 並行書き込みレース | briefing (cron 8:30 append) と timekeeper (対話 Write) が同一 `07-Daily/YYYY-MM-DD.md` に書く。T1a で保存先を統合した副作用。単一ユーザーで秒単位の衝突かつ復旧可能なため未対処 | 顕在化したら per-file lock (flock) |
| substring ヒューリスティック | double-management の title 一致は CJK 語境界判定不能のため部分文字列一致。4文字未満はガードしたが中程度長の誤検知は残存 | title 命名規約で下限を上げる / warning 扱いで人間が weekly-review で確認 |
| 07-Daily の混在 | briefing/plan/review/report が同フォルダに集約 (report のみ `-report.md`)。「時間ブロックは daily note、status/期日は task note」で真実は分離だが、フォルダ内の視覚的混在は残る | Bases 移行時に type 別ビューで整理 |
| Feb-2026 orphan | sync-daily-report リネーム前に `07-Daily/YYYY-MM-DD.md` として同期された旧日報が残存しうる (daily-reports は 2026-02 で停止)。Vault 実体に触れないため未掃除 | 手動 or 別タスクで棚卸し |
