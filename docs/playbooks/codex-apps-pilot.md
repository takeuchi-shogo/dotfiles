# Codex Apps Pilot

Codex の Apps / connectors を dotfiles で試すときの playbook。

## Goal

- `features.apps` を常時有効化する前に、pilot として安全に試す
- MCP と Apps の役割を混ぜず、外部接続の責務を整理する
- approval / sandbox / data exposure の前提を先に固定する

## When To Use

- `features.apps` または `features.apps_mcp_gateway` を試したい
- `/apps` で connector を使う workflow を設計したい
- MCP server ではなく ChatGPT Apps / connectors の方が向くか判断したい

## Start Small

1. user-level config を常時変更する前に、CLI one-off override で試す
2. まず 1 つの app / connector だけに絞る
3. destructive action ではなく read-heavy なユースケースから始める

## Suggested Pilot Flow

1. 目的を 1 文で定義する
2. 既存の MCP / skill / script で足りない理由を確認する
3. `codex --enable apps` で単発 session として起動する
4. 必要なら `features.apps_mcp_gateway` は別セッションで試す
5. `/apps` で対象 connector を選び、実際の prompt で利用する
6. 使えたことより、approval friction と出力の再現性を記録する

## One-Off Session

```sh
codex --enable apps
```

- 常時有効化の前に、まず 1 session だけで `/apps` の surface を確認する
- connector 選定は 1 つだけに絞る
- `features.apps_mcp_gateway` は別 session で評価する
- `codex exec --enable apps` は pilot 実行より観測用途に留める
- connector discovery や id 選定は interactive CLI の `/apps` を優先する

## Interactive Discovery

- `/apps` では `Installed <n> of <m> available apps` が表示される
- install 済みでない app は `Can be installed` と表示される
- install 前でも app 名と短い説明までは確認できる

## Install Flow

- app を選ぶと `Install on ChatGPT` の導線が出る
- install は browser 側で行い、その後 Codex に戻って続行する
- newly installed apps は `/apps` に出るまで数分かかることがある
- install 後は `$` で app を prompt に挿入する

## Persisted Config Pattern

常時有効化が必要になった場合も、all-on ではなく deny-by-default で始める。

```toml
[features]
apps = true

[apps._default]
enabled = false
destructive_enabled = false
open_world_enabled = false

[apps."<app-id>"]
enabled = true
default_tools_enabled = true
default_tools_approval_mode = "prompt"
destructive_enabled = false
open_world_enabled = false
```

- `apps._default.enabled = false` で未評価 connector を閉じる
- `default_tools_approval_mode = "prompt"` で app tool call を明示確認に寄せる
- write-heavy tool を使うまで `destructive_enabled` と `open_world_enabled` は `false` のままにする
- 必要なら `apps.<id>.tools.<tool>.enabled` と `apps.<id>.tools.<tool>.approval_mode` で tool 単位に絞る

## Good First Pilots

- docs / knowledge source の参照
- issue tracker や project tracker の read-only lookup
- file search や status check のような read-heavy task

## Avoid In First Pilot

- write や delete を伴う app tool
- secret や個人情報を広く含む prompt
- 複数 app を同時に有効化する大きい workflow
- MCP と Apps を同時に増やして、原因切り分け不能にすること

## Validation

- `codex features list`
- `task validate-configs`
- `.codex/config.toml` を変えた場合は `task validate-symlinks`

## Decision Rules

- repo 固有の repeatable workflow なら skill や MCP を優先する
- 認証済みの external system をすぐ使いたいなら Apps を検討する
- pilot が 2 回以上再利用されるなら、plan から playbook か skill へ昇格する
- 常時有効化する前に、対象 app、approval pattern、rollback 方針を決める

## Watchouts

- Apps は MCP の代替ではなく別の external context surface
- approval / sandbox の前提は session ごとに確認する
- 実際の maturity は docs より `codex features list` を優先する
- gateway 系 feature は単体 Apps pilot と分けて評価する
- destructive annotation を持つ app tool は shell command でなくても approval 対象になりうる
- `codex exec` は `/apps` のような interactive discovery surface を置き換えない
- first pilot で install が必要なら、実利用の前に browser 往復と reload を見込む
