# agent-browser Server Lifecycle Notes

> 出典: Warp `oz-skills/webapp-testing` (2026-05-06 absorb) の運用パターンを agent-browser 文脈に翻訳。
> アーキ選択は agent-browser のまま（Playwright への乗り換えではない）。

`/webapp-testing` を使うとき、サーバ起動と検証順序で踏みやすい罠を 2 行で codify する。

## Rule 1: 先に `--help` を読む（CLI-first discovery）

`agent-browser` の subcommand を使う前に必ず `agent-browser --help` / `agent-browser <cmd> --help` を読む。訓練データに含まれない更新（snapshot 形式の変更、新 flag）は help にしか書かれていない。

```bash
agent-browser --help
agent-browser snapshot --help
agent-browser open --help
```

トリガー: 「`agent-browser` コマンドが期待動作と違う」「flag が認識されない」「snapshot 形式が想定と違う」

## Rule 2: 動的 app は reconnaissance-then-action

サーバが SPA / SSR / WebSocket を含む動的 app の場合、いきなり click/type せず **必ず先に snapshot を取って構造を確認する** （recon）。snapshot で role/aria 構造を把握してから操作する。

```
NG: agent-browser click "submit"  # ← 先に snapshot していない
OK:
  1. agent-browser snapshot   # accessibility tree 取得
  2. 構造確認 → 適切な ref 特定
  3. agent-browser click <ref>
```

理由: 動的 app は initial render 前 click で「見えない要素」を踏む。snapshot は accessibility-tree ベースで render 完了を待つため、安全。

## サーバライフサイクル

agent-browser は agent-browser 自身がサーバ管理を行わないため、開発サーバは **テスト前に手動起動**:

```bash
# 別ターミナル or background で:
npm run dev &
# その後 agent-browser で接続
agent-browser open http://localhost:3000
```

長時間 polling を agent-browser 内でやらない（無限 spin の原因）。完了確認は外部 monitor（`Monitor` tool）を使う。

## Warp の `with_server.py` を採用しない理由

Warp `oz-skills/webapp-testing` は `with_server.py` ヘルパで Python 経由で server を fork-管理するが、当 dotfiles は agent-browser CLI スタックを選択している。Python ラッパを足すと:
- アーキの 2 重化
- 起動失敗時の診断経路が増える
- skill description token tax が重くなる

→ サーバ管理は OS / 既存 dev script に任せ、agent-browser は接続のみ担当する境界を維持する。

## 関連

- `/webapp-testing` (skill) — メインスキル
- `references/cli-first-discovery.md` (もしあれば) — `--help` ファースト原則
