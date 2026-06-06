---
name: dispatch
description: "cmux Worker Router — タスクをサブエージェントまたは cmux Worker (Claude Code / Codex / Gemini) に振り分けて実行する。長時間タスク・マルチモデル・高並列の場合に cmux Worker を使用。self-improve preset (/improve 後継): 各軸 Skill を cmux ペインで並列起動し提案を集約する自己改善ループ。Triggers: 'dispatch', '振り分けて', 'Worker で実行', 'cmux で', 'Gemini に投げて', 'Codex に投げて', '別のモデルで', '長時間タスク', 'バックグラウンドで', '並列で実行', 'route this task', '改善ループ', 'self-improve', 'self improve', '自己改善'. Do NOT use for: 単純なサブエージェント委譲（use Agent tool directly）、リサーチ（use /research）、単発の Codex/Gemini 質問（use /codex or /gemini directly）。"
origin: self
user-invocable: true
metadata:
  pattern: tool
  chain:
    upstream: ["/spec (タスク定義)"]
    downstream: ["/codex", "/gemini", "Agent tool"]
---

# /dispatch — cmux Worker Router

タスクを受けて「サブエージェント or cmux Worker」を判定し、適切な実行環境で起動する。

## 判定フロー

以下の順序で判定する。最初にマッチした条件で実行先を決定:

1. **5分以内 & 構造化結果が必要** → サブエージェント（Agent tool）
2. **Codex 向きタスク** → cmux Codex Worker
   - 実装前リスク分析、セキュリティ深掘り、設計判断、トレードオフ分析
   - 複雑デバッグ、コードレビュー（100行以上）、Plan 批評
   - 参照: `rules/codex-delegation.md`
2.5. **race モード** → 複数モデル並列実装で最速を採用
   - 条件: プロンプトに "race" / "競争" / "複数モデルで" が含まれる、またはユーザーが明示的に race を要求
   - 対象: M規模以上の実装タスク（S規模はコスト見合わず単一モデル）
   - 実行: `scripts/runtime/race-runner.sh --task "..." --models claude,codex`
   - 結果: 最初に完了した Worker の実装を採用。残りは自動クリーンアップ
   - cmux 外の場合: 単一モデルにフォールバック（race 不可の旨を通知）
3. **Gemini 向きタスク** → cmux Gemini Worker
   - コードベース全体分析（200K超）、外部リサーチ（Google Search grounding）
   - マルチモーダル処理（PDF/動画/音声）、ドキュメント全体分析
   - 参照: `rules/gemini-delegation.md`
4. **30分以上 or 人間介入の可能性** → cmux Claude Code Worker (⚠ 2026-06-15 以降、Worker が `claude -p`/SDK 起動形態なら Agent SDK credit 消費。Codex/Gemini Worker は独立予算で credit 対象外: `references/agent-sdk-credit.md`)
5. **5+ 並列タスク** → cmux Worker（モデルはタスク性質で選択）
6. **それ以外** → サブエージェント（デフォルト）

## 使い方

```
/dispatch タスク内容をここに記述
```

### 並列タスクリスト形式

番号付きリストで複数タスクを渡すと、各タスクを独立した Worker で並列実行する:

```
/dispatch
1. brands ページにエクスポートボタンを追加
2. deals ページのページネーションバグを修正
3. CampaignController のテストを追加
```

**自動処理**:
- 各タスクに worktree を自動作成（`feature/{task-slug}`）
- 各 Worker に Awareness Summary を自動注入（`references/subagent-delegation-guide.md` 参照）
- 全 Worker 完了後にコンフリクト検出を実行

**Awareness Summary 自動注入例**:
```
## Awareness Summary
他のエージェントが並行して以下の作業をしています:
- Worker 2: deals ページのページネーションバグ修正（src/pages/deals/）
- Worker 3: CampaignController のテスト追加（tests/controllers/）

あなたの担当外のファイルには触れないでください。
```

## 実行手順

### Worker プロンプト品質ルール（全方式共通）

Worker は親の会話を見れない。プロンプトは必ず**自己完結**させる:

- リサーチ結果を自分で合成してから具体スペック（ファイルパス+行番号+型情報）を渡す
- 「Based on your findings」「Based on the research」は禁止 — 理解の丸投げ
- 「done」の定義を明示する（例: 「テスト実行+コミット+ハッシュ報告」）
- リサーチ指示なら「ファイルを変更するな」を明示

```
BAD:  "Based on the research, fix the auth bug"
GOOD: "Fix the null pointer in src/auth/validate.ts:42.
       Session.user is undefined when expired. Add nil check
       before user.id — if nil, return 401. Commit and report hash."
```

### サブエージェントに振り分ける場合

通常の Agent tool で実行する。特別な手順なし。

### cmux Worker に振り分ける場合

<IMPORTANT>
cmux 内で実行していることを確認すること。`CMUX_WORKSPACE_ID` 環境変数が設定されていない場合は cmux 外なのでサブエージェントにフォールバックする。
</IMPORTANT>

**Step 1: Worker を起動する**

Bash tool で `launch-worker.sh` を実行:

```bash
# Claude Code Worker の場合
scripts/runtime/launch-worker.sh --model claude --task "タスク内容" --worktree feature/branch-name

# Codex Worker の場合
scripts/runtime/launch-worker.sh --model codex --task "タスク内容"

# Gemini Worker の場合
scripts/runtime/launch-worker.sh --model gemini --task "タスク内容"
```

出力される `workspace_id` と `worker_id` を記録する。

**Step 2: 結果を回収する**

Bash tool で `collect-result.sh` を実行:

```bash
scripts/runtime/collect-result.sh --workspace <workspace_id> --worker <worker_id> --timeout 1800
```

- 完了: 結果テキストが stdout に出力される
- タイムアウト: exit code 2
- エラー: exit code 1（リトライ上限超過）

**Step 3: 結果をユーザーに報告する**

回収した結果をユーザーに要約して報告する。

### 複数 Worker を並列起動する場合

複数の `launch-worker.sh` を Bash tool で並列実行し、その後 `collect-result.sh` をそれぞれ実行する。

```bash
# 並列起動
WS1=$(scripts/runtime/launch-worker.sh --model claude --task "API実装" --worktree feature/api)
WS2=$(scripts/runtime/launch-worker.sh --model codex --task "セキュリティ分析")

# 結果回収（それぞれバックグラウンドで）
scripts/runtime/collect-result.sh --workspace $(echo $WS1 | cut -d' ' -f1) --worker $(echo $WS1 | cut -d' ' -f2) &
scripts/runtime/collect-result.sh --workspace $(echo $WS2 | cut -d' ' -f1) --worker $(echo $WS2 | cut -d' ' -f2) &
wait
```

### self-improve preset（自己改善ループ）

`/improve`（retire 2026-05-03）の後継。各軸の専門 Skill を cmux ペインで**並列起動**し、各ペインは**提案を返すだけ**（確定しない）。集約・採否・確定はメイン Claude + 人間に残す（無人確定 = Goodhart を回避）。

**トリガー**: ユーザーが「改善ループ回して」「self-improve」等と言ったとき。

**提案は stdout でなく JSON ファイルで受け渡す**。stdout 回収 (collect-result) は worker のサイレント終了や長文埋もれで不確実なため、各 worker は固定パスに提案を Write し、オーケストレーターはそのファイルを読む (あれば成功 / なければ失敗が明示的)。出力先は `.triage/self-improve/` (`.triage/` は .gitignore 済)。

**Step 0: 出力ディレクトリを用意**:
```bash
DATE=$(date +%F); OUT=".triage/self-improve/$DATE"; mkdir -p "$OUT"; rm -f "$OUT"/*.json
```

**Step 1: 3 軸を並列起動**（cmux 内のみ。外なら各 Skill を順次手動実行にフォールバック）。各 worker は提案を **JSON ファイルに Write** し、完了したら stdout に `DONE <path>` だけ出す:

```bash
HC=$(scripts/runtime/launch-worker.sh --model claude --task "/check-health を実行し doc 鮮度・参照整合性の問題を検出する。**ファイルを編集・commit しない (提案のみ)。** 提案を $PWD/$OUT/check-health.json に Write せよ (形式: {\"axis\":\"check-health\",\"proposals\":[{\"target\":\"<path>\",\"change\":\"<何を直すか>\",\"evidence\":\"<file:line>\"}],\"status\":\"complete\"})。Write 後 stdout に 'DONE $OUT/check-health.json' とだけ出す。")
SA=$(scripts/runtime/launch-worker.sh --model claude --task "/skill-audit を実行し skill の health・description 衝突を検出する。**編集しない (提案のみ)。** 提案を $PWD/$OUT/skill-audit.json に Write (同形式, axis=skill-audit)。Write 後 'DONE' を出す。")
PL=$(scripts/runtime/launch-worker.sh --model claude --task "/auto-triage を実行し learned 昇格候補を分類する。**昇格 (artifact 編集) は人間が /promote-learnings で確定 (提案のみ)。** 提案を $PWD/$OUT/promote-learnings.json に Write (同形式, axis=promote-learnings)。Write 後 'DONE' を出す。")
```

**Step 2: 完了待ち**（collect-result で各 worker の DONE を待つ。stdout は短いので埋もれない）:

```bash
for WS in "$HC" "$SA" "$PL"; do
  scripts/runtime/collect-result.sh --workspace "$(echo "$WS" | cut -d' ' -f1)" --worker "$(echo "$WS" | cut -d' ' -f2)" --timeout 1800 &
done
wait
ls -1 "$OUT"/*.json   # 揃った提案ファイルを確認 (3 つ揃わなければ欠けた軸が失敗)
```

**Step 3: メイン Claude が集約** — `$OUT/*.json` を Read して 3 軸の `proposals` を統合し、重複・矛盾を整理してユーザーに提示する。**ファイルが欠けている軸は「失敗」として明示する** (sailent fail 禁止)。stdout が DONE でも JSON が無ければ worker が Write に失敗している。

**Step 4: 人間が採否** — ユーザーが採用する提案を選ぶ。採用分のみメイン Claude が確定（Edit/commit/PR）。

**Step 5: 完了** — 全提案を採否し終えたら cmux ペインを閉じる。これがループ完了。

**設計上の制約（Codex 批評由来、2026-06-06）**:
- **自動再問い合わせループは作らない** — `status:needs_followup` でも再問い合わせは人間判断で手動。無人ループは backlog 生成装置になる（最大の失敗モード）
- **3 軸固定**（check-health / skill-audit / auto-triage）— 全 6 軸同時起動は YAGNI。review/audit/absorb が要るなら手動で足す
- **各ペインは提案のみ**、確定（Edit/commit/PR）はメイン + 人間。これが `/improve` の無人確定（Goodhart）を回避する核心
- **責任点を明示** — 提案は必ず採否してから閉じる。未採否で放置しない（backlog 生成装置化を防ぐ）

## 通信ログ

全通信は自動的に `/tmp/cmux-dispatch-log/` に JSONL 形式で記録される。

```bash
# ログ閲覧
scripts/runtime/dispatch-log.sh show

# 特定ワーカーのフィルタ
scripts/runtime/dispatch-log.sh filter --worker <worker_id>

# サマリ
scripts/runtime/dispatch-log.sh summary
```

## cmux 外での挙動

cmux 外で実行された場合、全てサブエージェントにフォールバックする。cmux Worker 機能は無効化される。

## Anti-Patterns

- **大規模 fan-out をいきなり全量で回す**: 200-2000 ファイル級の移行を一発で投入すると、共通の失敗パターン (環境前提誤り / API rate limit / 部分的な型差異) を全 Worker が同時にヒットする。先に 3-5 ファイルでパイロット実行し、失敗パターンを潰してから本番展開する。Codex/Gemini Worker でも同じ。

> 出典: Boris Tip 22 absorb (2026-04-30) — 「いきなり全量で回さない、まず数ファイルで失敗パターンを洗い出してから全体に展開」
