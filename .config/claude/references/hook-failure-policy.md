---
status: reference
last_reviewed: 2026-05-30
---

# Hook Failure Policy (fail-open / fail-closed カタログ)

`hook_utils.run_hook(hook_name, main, *, fail_closed=...)` が **想定外の例外時**にどう振る舞うかの一覧。
目的は auditability — 「どの hook が壊れたとき素通り (fail-open) し、どの hook が block (fail-closed) するか」を 1 ファイルで legible にする。

**single source は code** (`run_hook` 呼び出し)。本ファイルはそのスナップショット。乖離検出には下の再生成コマンドを使う。

## 挙動の定義 (`scripts/lib/hook_utils.py`)

- `fail_closed=True` — 例外時に `BLOCKED: ... failed-closed` を stderr に出し **exit 2** (操作をブロック)。security/policy gate が静かにバイパスされるのを防ぐ。
- `fail_closed=False` (明示) / **省略時の既定** — 例外時に `{}` を stdout に出して **素通り (fail-open)**。advisory hook が壊れても開発を止めない。
- いずれも `SystemExit` (= main 内の明示的 `sys.exit(2)` による正規のブロック判定) はそのまま re-raise される。fail_closed は「正規のブロック」ではなく「**予期しないクラッシュ時**」の方針である点に注意。

## 選択原則 (codify)

1. **security / policy gate (違反時に exit 2 で block する hook) → `fail_closed=True`**。
   壊れて素通りすると禁止操作が通ってしまうため。例: prompt-injection / docker-safety / mcp-audit。
2. **advisory hook (warn・ログ・context 注入のみで block しない hook) → `fail_closed=False` (または省略)**。
   そもそも block しないので、クラッシュ時に素通りさせる方が開発体験を阻害しない。
3. 迷ったら「この hook が**何も検査しなかった**ら危険か？」で判断する。危険なら True。

## カタログ (30 callers: True 6 / 明示 False 12 / 省略=False 12)

| hook | fail_closed | 分類 | event |
|------|-------------|------|-------|
| docker-safety | **True** | security-gate | PreToolUse |
| mcp-audit | **True** | security-gate | PreToolUse |
| prompt-injection-detector | **True** | security-gate | PreToolUse |
| derivation-honesty-hook | **True** | policy-gate | PostToolUse |
| gaming-detector | **True** | policy-gate | PostToolUse (indirect) |
| rationalization-scanner | **True** | policy-gate | PostToolUse |
| approval-fatigue-guard | False | policy-advisory | PostToolUse |
| diff-coverage-gate | False | policy-advisory | Stop |
| file-proliferation-guard | False | policy-advisory | PostToolUse |
| impact-scan | False | policy-advisory | PostToolUse |
| mcp-response-inspector | False | policy-advisory | PostToolUse |
| memory-integrity-check | False | policy-advisory | SessionStart |
| plan-implement-bridge | False | policy-advisory | (indirect) |
| spec-quality-check | False | policy-advisory | PostToolUse |
| tdd-guard | False | policy-advisory | (indirect) |
| tool-scope-enforcer | False | policy-advisory | (indirect) |
| type-safety-delta | False | policy-advisory | PostToolUse |
| user-input-guard | False | policy-advisory | UserPromptSubmit |
| agent-invocation-logger | 省略(=False) | observability | PostToolUse |
| golden-check | 省略(=False) | policy-advisory | PostToolUse (indirect) |
| mcp-skill-hint | 省略(=False) | advisory | PostToolUse |
| output-offload | 省略(=False) | observability | (indirect) |
| plan-lifecycle | 省略(=False) | lifecycle | (indirect) |
| post-test-analysis | 省略(=False) | observability | (indirect) |
| skill-tracker | 省略(=False) | observability | PostToolUse |
| stagnation-detector | 省略(=False) | policy-advisory | PostToolUse |
| structure-check | 省略(=False) | policy-advisory | PostToolUse |
| subagent-monitor | 省略(=False) | observability | SubagentStop |
| suggest-gemini | 省略(=False) | advisory | (indirect) |
| webfetch-truncation-detector | 省略(=False) | observability | PostToolUse |

> 「(indirect)」= settings.json の hooks に直接登録されず、別 hook / wrapper / Task 経由で起動するもの。
> event の権威ソースは `settings.json` の `hooks` ブロック。

## 監査の観察 (2026-05-30)

- **fail_closed=True の 6 件は全て security/policy gate** で原則 1 に整合 (PreToolUse 3 + PostToolUse 3)。
- block しない advisory/observability hook は全て fail-open。原則 2 に整合。
- 新規 hook 追加時は分類 (block するか) を判定し、本表に 1 行追加する。block する security gate なら必ず `fail_closed=True`。

## 再生成 (drift チェック)

```bash
# fail_closed 値の一覧 (single source)
grep -rhn 'run_hook("' .config/claude/scripts/ --include="*.py" | grep -v 'def run_hook'
# event 配置の権威ソース
python3 -c "import json;d=json.load(open('.config/claude/settings.json'));[print(ev,h.get('command')) for ev,a in d['hooks'].items() for m in a for h in m.get('hooks',[])]"
```
