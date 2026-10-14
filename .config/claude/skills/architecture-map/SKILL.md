---
name: architecture-map
description: >
  リポジトリを読み、C4 モデルで Level1→2→3 の動的アーキテクチャ図（ドリルダウン HTML +
  ユースケース再生）を段階的に作る。Triggers: 'アーキテクチャ図', 'C4', 'architecture map',
  '動的アーキテクチャ', 'ドリルダウン', '構成図', 'コンテナ図', 'ユースケースの流れ'.
  Do NOT use for: 知識グラフ探索のみ（use explore-codebase）、単一ファイルのクラス図だけ、
  実装変更そのもの。
origin: self
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Agent, AskUserQuestion
user-invocable: true
metadata:
  pattern: pipeline
  version: 1.0.0
  category: analysis
  source: "https://techblog.recerqa.com/blog/20261013-dynamic-architecture-diagram/"
---

# /architecture-map — C4 動的アーキテクチャ図

リポジトリを根拠に C4 モデルの図を **Level1 から一段ずつ** 足し、ドリルダウンできる HTML
マップと、Level2 上のユースケース再生（コミュニケーション図）まで作る。

## なぜ Skill があるか

出典記事の著者は、最近のモデル（例: Opus 5.5）なら Skills 無しでも図を描けると書いている。
この Skill の役割は「描けるかどうか」ではなく、**同じ手順を毎回繰り返せる契約**にする
こと（確認ゲート・成果物の形・explore-codebase との分担）。

## explore-codebase との違い

| | `/architecture-map` | `explore-codebase` |
|---|---|---|
| 目的 | C4 図と操作可能な HTML マップ | 知識グラフでの構造探索 |
| 出力 | Level1–3 図、ドリルダウン HTML、ユースケース再生 | graph MCP の stats / communities / flows |
| 図 | 描く（draw.io / HTML） | 描かない |

グラフでモジュールを辿るだけなら `explore-codebase`。全体像を縮尺つきの図で共有・再生するなら本 Skill。

## C4 レベルの約束（出典どおり）

- **Level1** System Context: システムを1箱、利用者と外部システムとの関係
- **Level2** Container: アプリ・DB など「動いている必要がある単位」とそのつながり（Docker コンテナではない）
- **Level3** Component: 1 コンテナ内の主要部品と役割
- **Level4** Code: 出典でも任意とし、今回は扱わない（IDE で都度生成）

補助: 処理の流れは Level2 上のコミュニケーション図（ユースケース再生）として作る。

## Workflow

```
/architecture-map {repos or cwd}
  1. Read repos     → アプリ / デプロイ / インフラ等、指定リポジトリを徹底参照
  2. Level1 draw    → System Context を描き、人間に確認してから次へ
  3. Level2 add     → 確認済み Level1 にドリルダウンする Container 図を足す
  4. Level3 add     → 中身が複雑なコンテナから Component 図を足す
  5. Drill-down HTML → Level1→2→3 を辿れるマップ（選択で説明表示）
  6. Use-case play  → Level2 上でユースケース手順を順再生できる HTML
```

### Step 1: Read repos

指定されたリポジトリ（アプリ・デプロイ設定・インフラなど）を根拠にする。
推測で箱を増やさない。出典にない要素は「未確認」と明示する。

### Step 2: Level1 → 確認ゲート

まず Level1 だけ描く。**人間の確認前に Level2/3 へ進まない。**

出力の目安（記事のプロンプトに合わせる）:

- 出力先が指定されていれば draw.io（または同等の編集可能な図）
- 配置は描画して確かめながら調整する

確認で直すのは「箱の境界」と「外部との関係」。細部の見た目は後回し。

### Step 3–4: Level2 / Level3 を一段ずつ

Level1 確認後に「Level2 も描く」。Level3 は「まずは中身が複雑なコンテナから」。
一気に全部を埋めない。

### Step 5: ドリルダウン HTML

Level1→Level2→Level3 を辿れる HTML アーキテクチャマップを作る。出典の操作契約:

- 全体表示から、詳細図のある要素を **ダブルクリック** で1つ下の階層へ
- 箱を選ぶと、図からは読み取れない **目的・機能** の説明を表示する
  （システムをあまり知らない人でも分かる説明）

### Step 6: ユースケース再生（Level2 上）

Level2 図の上で、ユースケースごとの処理の流れを1ステップずつ再生できる HTML を作る。
出典の操作契約:

- 手順クリック、または「順に再生」で矢印と説明を出す
- 関係するコンテナだけを濃く表示する
- 同期呼び出しか非同期（キュー・イベント・定期実行）かを線の種類で区別する

ユースケースの洗い出しもリポジトリ調査に基づく。シーケンス図単体に逃げず、
**構成の中を処理が流れる様子**が見えることを優先する。

## 任意の追加図（ほしくなったとき）

出典で「コストが低いので足している」例。必須ではない。

- インフラ構成図（C4 のデプロイ図に近いもの）
- Level2 粒度のデプロイ順序（CI 依存・マイグレーション順から制約を洗う）

## Anti-patterns

- ✗ Skills 無しで一発 Level3 まで描いて終わり → ✓ Level1 確認 → 一段ずつ足す
- ✗ draw.io をファイルごとに開いて終わり → ✓ ドリルダウン HTML まで作る
- ✗ シーケンス図だけで「動き」を説明する → ✓ Level2 上の再生で構成と動きを同じ画面に載せる
- ✗ `explore-codebase` の graph 探索と混同する → ✓ 図が要るなら本 Skill、グラフ探索ならあちら
- ✗ リポジトリに無い箱・依存を補完する → ✓ 根拠のない関係は書かないか「未確認」と刻む

## 成果物チェックリスト

- [ ] Level1 を描き、確認を取った
- [ ] Level2（必要なら Level3）を確認後に追加した
- [ ] Level1→2→3 ドリルダウン HTML（選択時説明つき）
- [ ] Level2 上のユースケース再生 HTML（同期/非同期の線分け）
- [ ] 根拠にしたリポジトリパスを報告に書いた

## 出典

- ももっち / RECERQA Tech Blog「動的アーキテクチャ図のすすめ」(2026-10-13)
  https://techblog.recerqa.com/blog/20261013-dynamic-architecture-diagram/
