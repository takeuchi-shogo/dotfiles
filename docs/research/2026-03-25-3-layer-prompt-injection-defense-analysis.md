---
source: https://creators.bengo4.com/entry/2026/03/24/080000
date: 2026-03-25
status: analyzed
---

## Source Summary

**Title**: Claude Code / CursorのHooksで実装したAIエージェントの3層プロンプトインジェクション対策
**Author**: 藤谷（クラウドサイン CRE担当）
**Published**: 2026-03-24

### 主張
LLMに「気をつけて」と指示するのではなく、LLMの外側にある実行境界（Hooks）で止める設計思想。3層防御 + 段階的デプロイで運用リスクを最小化。

### 手法
1. **3層 hook 構造**: UserPromptSubmit(入力) → PreToolUse(実行前, 主軸) → PostToolUse(出力)
2. **Layer 1**: ジェイルブレイク検出 — ignore previous instructions, reveal system prompt, base64指示, `<system>`タグ偽装
3. **Layer 2**: 危険コマンドブロック — curl|bash, rm -rf /, keychain, gh auth token
4. **Layer 2**: 機密ファイルアクセス検出 — .env, ~/.aws/credentials, ~/.ssh/id_*
5. **Layer 2**: MCP破壊操作ブロック — delete, drop, truncate, 未知ホスト
6. **Layer 3**: ツール出力スキャン — PostToolUseでフラグ → 次のPreToolUseでブロック
7. **Dual-mode検査**: raw版 + sanitized版（クォート/heredoc除去）でOR判定
8. **3段階デプロイ**: audit(ログのみ) → warn(警告) → block(ブロック)
9. **fail-closed**: フック異常時もブロック維持
10. **構造化ログ**: タイムスタンプ + イベント + 理由の構造化記録
11. **チーム展開**: setup.sh + jq マージで個人設定を保持

### 根拠
- Google ドキュメント内の不可視テキストに削除コマンドを仕込むデモで有効性を実証
- 設計4原則: 主軸の明確化、dual-mode検査、fail-closed、段階的投入

### 前提条件
- Claude Code または Cursor 2.4+
- AIエージェントがファイル読取・コマンド実行・外部API呼出を自動実行する環境

## Gap Analysis

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | Layer 1: UserPromptSubmit でのジェイルブレイク検出 | **Partial** | UserPromptSubmit は agent-routing のみ。インジェクション検出は PreToolUse の prompt-injection-detector.py にあるが、ユーザー入力段階では走っていない |
| 2 | Layer 2: 危険コマンドブロック (curl\|bash, rm -rf /, keychain, gh auth token) | **Partial** | /careful スキルがオプトインで rm -rf 等をブロック。常時有効ではない |
| 3 | Layer 2: 機密ファイルアクセス検出 (.env, ~/.aws/credentials, ~/.ssh/id_*) | **Gap** | hook レベルでの機密ファイルアクセス検出なし。security rules は instruction ベースのみ |
| 4 | Dual-mode検査 (raw + sanitized で OR判定) | **Gap** | 全検出器が raw テキストのみ検査 |
| 5 | 3段階デプロイ (audit → warn → block) | **Gap** | 各 hook が block or advisory で固定。運用モード切替なし |
| 6 | チーム展開 (setup.sh + jq マージ) | **N/A** | 個人 dotfiles。symlink で一元管理済み |

### Already 項目の強化分析

| # | 既存の仕組み | 記事が示す弱点/知見 | 強化案 |
|---|-------------|-------------------|--------|
| A | 3層 hook 構造 (全3イベント稼働) | 記事は Layer 2 を「主軸」と明確化 | Already (強化不要) |
| B | prompt-injection-detector.py (zero-width, ANSI, null byte, base64, nested cmd sub) | 記事は自然言語ジェイルブレイクも Layer 1 で検出 | **Already (強化可能)** — 自然言語パターン追加 |
| C | mcp-audit.py (destructive GitHub/filesystem ブロック) | 記事は truncate + 未知ホストもブロック | **Already (強化可能)** — パターン追加 |
| D | mcp-response-inspector.py (PostToolUse advisory) | 記事は PostToolUse→フラグ→次PreToolUseブロックのチェーン | **Already (強化可能)** — チェーン機構追加 |
| E | fail-closed (run_hook fail_closed=True) | 同等 | Already (強化不要) |
| F | JSONL構造化ログ | 同等 | Already (強化不要) |

## Integration Decisions

全7項目を取り込み:
1. [Gap] 機密ファイルアクセス検出
2. [Partial] UserPromptSubmit にジェイルブレイク検出追加
3. [Partial] 危険コマンドの常時ブロック
4. [Gap] Dual-mode 検査
5. [Gap] 3段階デプロイモード
6. [強化] mcp-audit.py に truncate + 未知ホスト検出
7. [強化] PostToolUse → PreToolUse ブロックチェーン

## Plan

### Task 1: prompt-injection-detector.py に機密ファイル + 危険コマンドパターン追加 (S)
- **ファイル**: `.config/claude/scripts/policy/prompt-injection-detector.py`
- **変更**: SENSITIVE_FILE_PATTERNS と DANGEROUS_BASH_PATTERNS を追加
- パターン: .env, ~/.aws/credentials, ~/.ssh/id_*, curl|bash, wget|bash, rm -rf /, security find-generic-password, gh auth token
- Bash ツールのみで適用（Edit/Write には不要）

### Task 2: prompt-injection-detector.py に dual-mode 検査追加 (S)
- **ファイル**: `.config/claude/scripts/policy/prompt-injection-detector.py`
- **変更**: `_sanitize(text)` 関数追加。クォート文字列・heredoc 内テキストを除去した版でも検査
- raw OR sanitized でマッチならブロック

### Task 3: 運用モード切替 (HOOK_GUARD_MODE) 追加 (S)
- **ファイル**: `.config/claude/scripts/policy/prompt-injection-detector.py`
- **変更**: `HOOK_GUARD_MODE` 環境変数で audit/warn/block を切替
- hook_utils.py の run_hook に mode パラメータを追加するか、スクリプト内で処理

### Task 4: UserPromptSubmit にジェイルブレイク検出 hook 追加 (M)
- **ファイル**: 新規 `.config/claude/scripts/policy/user-input-guard.py`
- **設定**: `.config/claude/settings.json` の UserPromptSubmit に追加
- パターン: ignore previous instructions, reveal system prompt, `<system>` タグ偽装
- 既存の agent-routing (Rust) とは別 hook として追加

### Task 5: mcp-audit.py 強化 (S)
- **ファイル**: `.config/claude/scripts/policy/mcp-audit.py`
- **変更**: DANGEROUS_MCP_PREFIXES に truncate パターン追加、未知ホスト警告ロジック追加

### Task 6: PostToolUse → PreToolUse ブロックチェーン (M)
- **ファイル**: `.config/claude/scripts/policy/mcp-response-inspector.py` (フラグ書込み)
- **ファイル**: `.config/claude/scripts/policy/prompt-injection-detector.py` (フラグ読取り)
- チェーン: PostToolUse 検出時にフラグファイル書込み → 次の PreToolUse でフラグ確認 → ブロック

### 依存関係
- Task 3 (モード切替) は Task 1, 2 と同時に適用可能
- Task 4 は独立
- Task 6 は Task 5 の後が望ましい（mcp-audit 強化後にチェーン追加）

### 規模推定: M（6ファイル変更）
