# Tool Scoping Guide — タスクスコープ別ツールサブセット

> Stripe Minions パターン: 500 ツールプールから各タスクタイプに必要最小限のツールのみを付与する。

## 1. 概要: なぜツールスコーピングが必要か

| 課題 | 説明 |
|------|------|
| **認知負荷** | 全ツールを渡すとエージェントがツール選択に迷い、不適切なツールを選ぶ確率が上がる |
| **トークン消費** | ツール定義自体がコンテキストウィンドウを消費する（ツール数に比例） |
| **安全性** | 調査タスクに Write/Edit が不要なら、アクセスを制限することで誤操作リスクを減らせる |
| **決定論性** | ツールセットが明示されていれば、同じタスクが同じツールで実行されやすくなる |

Stripe は 500 以上のツールプールから、タスクタイプごとに 5-15 のツールを選択して付与している。
我々の環境でも同様のパターンを、既存の `allowed-tools` メタデータを活用して実現する。

## 2. スコープの粒度

| レベル | 定義場所 | 例 | 強制度 |
|--------|---------|-----|--------|
| **Blueprint ノード** | `blueprints/*.yaml` の `tools` フィールド | `investigate` ノードは `[Read, Grep, Glob]` のみ | Phase 2 |
| **スキル** | SKILL.md の `allowed-tools` | `/spike` は `Read, Write, Edit, Bash, Glob, Grep, Agent, EnterWorktree` | advisory (warn) |
| **セッション** | `run-session.sh --allowedTools` | ヘッドレス実行時に物理制限 | enforced |
| **グローバル** | `settings.json` の deny rules | `rm -rf`, `git push --force` 等 | enforced |

**原則**: 上位レベルほど広く、下位レベルほど狭い。最終的な許可ツールは全レベルの共通部分。

## 3. Interactive vs Unattended の戦略

### Interactive（ユーザーが横にいる）

- **方針**: warn のみ（block しない）
- **理由**: ユーザーが判断できるため、block は UX を悪化させる
- **実装**: `tool-scope-enforcer.py` (PreToolUse hook) が stderr に警告を出力
- **exit code**: 常に 0（パススルー）

### Unattended（`claude -p` / ヘッドレス）

- **方針**: `--allowedTools` で物理的に制限（Stripe と同等のハードスコープ）
- **理由**: ユーザーの監視がないため、最小権限の原則を適用
- **実装**: `run-session.sh` が現在のコンテキストの `allowed-tools` を `--allowedTools` フラグに変換

```bash
# run-session.sh の例
claude -p "$prompt" --allowedTools "Read,Grep,Glob,Bash"
```

## 4. Blueprint との連携

Blueprint の各ノードが使用するツールを宣言する構想:

```yaml
# blueprints/investigate.yaml
nodes:
  search:
    tools: [Read, Grep, Glob]
    description: "コードベースの探索"
  analyze:
    tools: [Read, Grep, Glob, Bash]
    description: "テスト実行を含む分析"
  report:
    tools: [Read, Write]
    description: "レポート生成"
```

- `run-session.sh` がノード遷移を検出し、`--allowedTools` を動的に切り替える
- ノード遷移時にツールセットが変わることで、各フェーズの責務を物理的に分離

> **Note**: Blueprint の実行エンジンは Phase 2 で本格実装予定。
> 現時点ではスキルレベルのスコーピングを先行実装する。

## 5. MCP ツールのスコーピング

スキルの SKILL.md に `mcp-tools` メタデータを追加可能:

```yaml
---
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
mcp-tools: context7, brave-search
---
```

- `mcp-audit.py` がアクティブなスキルの `mcp-tools` をチェック
- スキル外の MCP server 使用は stderr に警告（advisory）
- MCP ツール名の形式: `mcp__<server>__<tool>` から `<server>` を抽出して照合

## 6. 設計判断

| 判断 | 理由 |
|------|------|
| `allowed-tools` は既存メタデータを活用 | 新概念を増やさない（KISS） |
| enforcer は PreToolUse hook | 既存 hook インフラに乗る。mcp-audit.py と同じパターン |
| Interactive は warn のみ (exit 0) | UX 優先。ユーザーが横にいるなら判断を委ねる |
| Blueprint スコープは Phase 2 | 実行エンジンが必要。現時点では過剰設計になる（YAGNI） |
| クールダウン 300 秒 | 同じ警告を繰り返さない（ログスパム防止） |
| `fail_closed=False` | advisory hook のため、エラー時も通過させる |

## 関連ファイル

- `scripts/policy/tool-scope-enforcer.py` — PreToolUse hook (advisory)
- `scripts/policy/mcp-audit.py` — MCP ツール監査 + スキルスコープチェック
- `skills/autonomous/run-session.sh` — `--allowedTools` によるハード制限
- `references/blueprint-pattern.md` — Blueprint 設計パターン
