# OpenAI Shell Pilot

OpenAI Hosted Shell / Local Shell を dotfiles 運用で試すときの playbook。

## Goal

- Hosted Shell と Local Shell の使い分けを固定する
- 初回は one-off pilot として試し、常用設定を急がない
- skill、network、artifact、background mode の境界を先に明文化する

## When To Use

- OpenAI API の shell tool を試したい
- Hosted Shell と Local Shell のどちらで運用すべきか判断したい
- repo 内 skill を OpenAI API skills として再利用できるか見極めたい
- artifact 生成や短時間の分析ジョブを OpenAI 側 container に寄せられるか確認したい

## Hosted Vs Local

- Hosted Shell を選ぶ
  - OpenAI 管理 container で再現性を優先したい
  - `/mnt/data` に artifact を出して回収する flow が中心
  - network を request ごとの allowlist で絞りたい
  - 内部 runtime や社内 filesystem へのアクセスは不要
- Local Shell を選ぶ
  - ZDR が必要
  - 既存の local filesystem、internal tooling、repo task を直接使いたい
  - 実行環境、permission、environment variable を自分で細かく制御したい

## Hard Constraints

- Hosted Shell は ZDR 非対応
- Hosted container は 20 分の inactivity で失効する
- Hosted artifact は `/mnt/data` 前提で扱う
- Hosted container は outbound network default deny なので、必要時だけ allowlist を明示する
- 初回 pilot で hosted と local を同時に評価しない

## Start Small

1. 目的を 1 文で定義する
2. hosted か local のどちらか片方だけ選ぶ
3. skill は 1 個まで、artifact も 1 個までに絞る
4. network が不要なユースケースから始める
5. 常用 config ではなく docs と one-off 実行手順を先に固める

## Suggested Pilot Flow

1. ユースケースを決める
2. hosted / local の選択理由を書く
3. skill を使うなら portable かどうかを先に確認する
4. network を要するかを確認し、要るなら allowlist 候補を最小化する
5. artifact の出力先と回収手順を決める
6. 長時間化しそうなら `background=true` を候補に入れる
7. 実行後は convenience ではなく、approval friction、再現性、回収手順の明確さで評価する

## Good First Pilots

- CSV やテキスト入力から Markdown report を 1 つ生成する
- skill 1 個を mount して `/mnt/data` に成果物を書かせる
- network なしで完結する軽い分析や整形を試す

## Avoid In First Pilot

- network allowlist と multi-skill を同時に入れる
- background mode が前提の長時間ジョブから始める
- repo 全体 clone や大量依存 install のような重い task
- ZDR 必須なのに Hosted Shell を選ぶ
- local shell で broad env inheritance を前提にする

## Hosted Shell Runbook

1. `environment.type="container_auto"` で開始する
2. artifact は `/mnt/data` に限定する
3. 複数 turn にまたがるなら `container_reference` を使う
4. container expiry を見込んで、必要な file は早めに回収する
5. network が不要なら `network_policy` を付けない
6. network が必要なら allowlist を最小化する

## Local Shell Runbook

1. `environment.type="local"` を使う
2. command 実行と `shell_call_output` の返却は自前 runtime で扱う
3. repo task や local tool を使う場合は、permission と env の前提を先に固定する
4. dotfiles に常用 profile を入れる前に one-off 実験で妥当性を確認する

## Skill Portability Checklist

- `SKILL.md` frontmatter に `name` と `description` があるか
- OpenAI API で読めない Codex 固有概念に依存していないか
- `.mcp.json`、subagent、slash command を前提にしていないか
- script が command line から deterministic に動くか
- output path が明示されているか
- repo 固有の task 名や path に強く結びついていないか

## Current Repo Guidance

- `.agents/skills/` は frontmatter 付きで構造は近い
- ただし `codex-search-first` のように MCP / subagent を前提にする skill は、そのままでは API-portable ではない
- `dotfiles-config-validation` のように repo task 前提の skill も Hosted Shell 向けには薄い adapter が必要になる
- first pilot 用の最小 bundle は `tools/openai-shell-skills/frontend-prompt-brief/` に分離した
- `openai-frontend-prompt-workflow` は reusable な source だが、Hosted Shell 向けには `frontend-prompt-brief` のような thin bundle に落として使う

## Background Mode

- 長時間ジョブだけに使う
- 初回 pilot では必要性が見えるまで通常 request を優先する
- 採用条件
  - polling を前提にしても運用が複雑化しない
  - response retention と ZDR 非互換を受け入れられる
  - foreground では timeout や接続不安定が現実に問題になる

## Evaluation Criteria

- hosted / local の選択理由が task と一致しているか
- skill が追加説明なしで発見・実行されるか
- artifact path と回収手順が明確か
- network allowlist が最小になっているか
- background mode が本当に必要か
- 2 回目も同じ runbook で再現できるか

## Validation

- playbook 更新時は `task validate-readmes`
- `.codex/config.toml` を触ったら `task validate-configs`
- `.codex/config.toml` を触ったら `task validate-symlinks`

## Watchouts

- Hosted Shell は repo 内 dotfiles 実行環境の代替ではない
- Local Shell は自由度が高いぶん permission 設計を雑にしやすい
- skill frontmatter 互換だけで portability を判断しない
- `/mnt/data` 前提の artifact flow を local shell にそのまま持ち込まない
- container expiry と artifact 一時性を docs に書かずに pilot を回さない
