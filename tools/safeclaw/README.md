# SafeClaw - コンテナ隔離 Claude Code 環境

Docker コンテナ内で Claude Code を実行し、autonomous / 実験環境のプロセス隔離を実現します。
[ykdojo/safeclaw](https://github.com/ykdojo/safeclaw) を参考にした設計です。

## 前提条件

- Docker Desktop または Docker Engine が稼働していること
- `CLAUDE_API_KEY` 環境変数が設定されていること

## クイックスタート

```bash
# 1. イメージのビルド
./scripts/build.sh

# 2. セッション起動
./scripts/run.sh

# 3. セッション停止
./scripts/stop.sh
```

## スクリプトオプション

### run.sh

```bash
# セッション名を指定
./scripts/run.sh -s my-experiment

# モデルを指定
./scripts/run.sh --model opus

# ホストの scripts/ を読み書きマウント（開発用）
./scripts/run.sh --mount-scripts
```

### stop.sh

```bash
# 特定セッションを停止
./scripts/stop.sh -s my-experiment

# 全セッションを停止
./scripts/stop.sh --all
```

## ディレクトリ構造

```
tools/safeclaw/
├── Dockerfile                      # コンテナ定義
├── docker-compose.yml              # compose 定義
├── scripts/
│   ├── build.sh                    # イメージビルド
│   ├── run.sh                      # セッション起動
│   └── stop.sh                     # セッション停止
├── config/
│   ├── .claude-container/
│   │   └── settings.json           # コンテナ専用設定
│   └── entrypoint.sh               # エントリポイント
└── README.md
```

## マウント構成

コンテナ起動時、ホストの dotfiles から以下が read-only でマウントされます:

| ホスト側パス                        | コンテナ内パス                          | モード |
| ----------------------------------- | --------------------------------------- | ------ |
| `.config/claude/CLAUDE.md`          | `/home/claude/.claude/CLAUDE.md`        | ro     |
| `.config/claude/references/`        | `/home/claude/.claude/references/`      | ro     |
| `.config/claude/skills/`            | `/home/claude/.claude/skills/`          | ro     |
| `.config/claude/agents/`            | `/home/claude/.claude/agents/`          | ro     |
| `.config/claude/scripts/` (opt-in)  | `/home/claude/.claude/scripts/`         | rw     |

## セキュリティ

- コンテナ内は非 root ユーザー `claude` で実行
- API キーは環境変数で注入（イメージに含めない）
- ホストのファイルシステムはデフォルトで read-only マウント
- `--mount-scripts` はホストの scripts を rw マウントするため、信頼できる環境でのみ使用

## docker-compose

```bash
# compose で起動
docker compose up -d

# ログ確認
docker compose logs -f

# 停止
docker compose down
```
