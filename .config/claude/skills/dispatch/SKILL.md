---
name: dispatch
description: cmux Worker Router — タスクをサブエージェントまたは cmux Worker（Claude Code / Codex / Gemini）に振り分けて実行する。長時間タスク・マルチモデル・高並列の場合に cmux Worker を使用。
user_invocable: true
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
3. **Gemini 向きタスク** → cmux Gemini Worker
   - コードベース全体分析（200K超）、外部リサーチ（Google Search grounding）
   - マルチモーダル処理（PDF/動画/音声）、ドキュメント全体分析
   - 参照: `rules/gemini-delegation.md`
4. **30分以上 or 人間介入の可能性** → cmux Claude Code Worker
5. **5+ 並列タスク** → cmux Worker（モデルはタスク性質で選択）
6. **それ以外** → サブエージェント（デフォルト）

## 使い方

```
/dispatch タスク内容をここに記述
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
