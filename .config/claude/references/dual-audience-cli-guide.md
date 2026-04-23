---
status: reference
last_reviewed: 2026-04-23
---

# Dual-Audience CLI Design Guide

CLI を人間とAIエージェントの両方から使えるように設計するための7原則。

Source: "Build a CLI for AI agents & humans in less than 10 mins" (ghchinoy, Saboo_Shubham_, Zack Akil)

## 原則 1: Structured Discoverability

コマンドごとに3フィールドを必ず定義する:

- **Short**: 1行要約（5-10語、動詞始まり）
- **Long**: 用途・他コマンドとの違い
- **Example**: 3-5個のコピペ可能な具体例

コマンドは機能グループで分類し、エントリポイントに `(start here)` を付ける。

AGENTS.md と skills/ で外部エージェント向けの明示的な指示を提供する。

## 原則 2: Agent-First Interoperability

```
# Human: formatted table
osa list

# Agent: structured JSON
osa list --json
```

- **`--json` on everything**: データを返す全コマンドに `--json` フラグを提供
- **自動検出**: `NO_COLOR`, `APP_NO_TUI` 環境変数、stdout がパイプ時は非対話モード
- **コンテキスト保護**: 巨大出力は自動 truncate、secret はマスク。`--full` で opt-in
- **プリソート**: 重要度の高い項目を先頭に配置

## 原則 3: Configuration and Context

- **XDG 準拠**: `~/.config/app/config.yaml`。ホームに dotfile を散らかさない
- **Named environments**: `--env local|staging|prod` で切替

```yaml
# ~/.config/app/config.yaml
default_env: "local"
envs:
  local:
    service_url: "http://127.0.0.1:9001"
  prod:
    service_url: "https://agent.example.com"
```

## 原則 4: Error Guidance

### Hint 行パターン

```
Error: database not initialized
Hint: run 'app init' to create the local database
```

エージェントは Hint 行をパースして自己修復する。人間はドキュメントを探す手間が省ける。

### 決定的 Exit Code

| Code | 意味 |
|------|------|
| 0 | Success |
| 1 | General error |
| 2 | Invalid usage / bad flags |
| 3 | Connection / auth failure |

**0 を返すのは成功した時だけ**。操作が失敗したのに 0 を返すと自動化が壊れる。

### Fail Fast

重い処理の前に config と接続を検証する。

## 原則 5: Flag & Argument Consistency

- **短縮形の統一**: `-o` が `--out-dir` なら全コマンドで同じ意味
- **Positional vs Optional**: 必須エンティティは positional、修飾子は `--flag`
- **安全なデフォルト**: デフォルトは最も安全なパス。破壊的操作は明示フラグ必須

## 原則 6: Semantic Color Tokens

色は状態を伝えるために使う。装飾ではない。

| Token | 用途 |
|-------|------|
| Accent | ヘッダ、セクションラベル |
| Command | コマンド名、フラグ |
| Pass | 成功状態 |
| Warn | 警告、進行中 |
| Fail | エラー、失敗 |
| Muted | メタデータ、デフォルト値 |
| ID | 一意識別子 |

ルール:
- 色は状態にだけ使う（緑=成功、黄=警告、赤=エラー）
- 説明テキストに色を付けない
- 階層はホワイトスペースで表現する
- ライト/ダーク両対応

## 原則 7: Versioning & Lifecycle

- `--version` で自バージョンを報告
- SIGINT (Ctrl+C) をグレースフルにハンドリング。データ破壊しない
- 書き込み操作では Actor を追跡（`$USER` or `git config user.name`）

## Hook/Script への適用

このリポジトリの hook スクリプトは Claude Code から呼ばれる。以下を適用する:

1. **Hint 行**: エラー時に `Hint:` プレフィックスで修復手順を出力 → Claude が自己修復
2. **Exit code**: 0/1/2 を区別（0=OK, 1=エラー, 2=使い方ミス）
3. **`--json` は不要**: hook の stdout は Claude が直接パースするため
