---
title: ターミナルツーリング
topics: [tooling]
sources: [2026-03-22-cmux-ecosystem-claude-code-analysis.md, 2026-03-22-ghostty-sand-cmux-analysis.md, 2026-04-02-dual-audience-cli-analysis.md, 2026-04-11-new-software-cli-skills-vertical-models-analysis.md, 2026-04-30-boris-30tips-absorb-analysis.md, 2026-05-15-cmux-customization-notes.md, 2026-05-31-personal-agent-stack-absorb-analysis.md, 2026-06-02-suzanne-teachback-absorb-analysis.md, 2026-06-02-typhoon-nix-mise-absorb-analysis.md]
updated: 2026-07-05
last_validated: 2026-07-05
source_count: 9
confidence: established
---

# ターミナルツーリング

## 概要

AI コーディングエージェントの長時間セッションに耐えるターミナル環境の設計と、人間・エージェント双方が使いやすい CLI の実装原則。Ghostty + cmux の組み合わせがエージェント特化ターミナルのデファクトとなりつつあり、デュアルオーディエンス設計によって同一 CLI が人間には TUI、エージェントには構造化データを返す。

## 主要な知見

- **VSCode terminal の限界**: M4 Mac でも Claude Code の長時間セッションでクラッシュする。Ghostty はネイティブ GPU レンダリングで AI スケールの出力に耐える
- **cmux のリソース階層**: `window → workspace → pane → surface`。pane（レイアウト）と surface（中身）の分離が従来マルチプレクサとの決定的な違い
- **Conductor/Worker 分離**: workspace:1 を Conductor（操作側・広いペイン）、workspace:2+ を Worker（実行側）に割り当て、詰め込みによる `read-screen` 破損を防ぐ
- **デュアルオーディエンス設計**: `--json` フラグで同一コマンドが人間には色付き TUI、エージェントには JSON/NDJSON を返す。コンテキストウィンドウ保護が前提
- **決定的 exit code**: 0/1/2/3 の標準化。エージェントは exit code でエラー種別を判断する
- **SAND mnemonic**: Split/Across/Navigate/Destroy の 4 操作にキーバインドを集約し、パネル管理を習慣化
- **OSC 通知統合**: cmux の OSC 9/99/777 シグナルを hooks に接続し、Stop/Notification イベントを統一的に処理
- **Error Hint 行**: CLI のエラーメッセージに次のアクションを示す Hint 行を添えることで、エージェントの自律回復を助ける
- **cmux 設定の4段階優先順位**: プロジェクトローカル `.cmux/cmux.json` (actions/commands/notificationsのみ上書き) > グローバル `~/.config/cmux/cmux.json` (全項目) > Settings UI 保存値 > legacy `settings.json`。JSONC形式（コメント・trailing comma許容）で `cmux config doctor` によりソケット不要でスキーマ検証できる
- **ツール表面の信頼性ラダーと操作の信頼ティア**: 「file/git/rg > 公式CLI/API > MCP > browser snapshot > screenshot/screen」という発見手段の信頼性軸と、「read > propose/draft > local write > commit > external side-effect(送信) > destructive」という操作の危険度軸は直交する。両方を明示することで、どのツールをどこまで自律実行させてよいかの判断が速くなる
- **Hook/Checkpoint の運用上の注意**: hook の実行時間が5秒を超えたら警告する仕組みが有効。checkpoint は外部副作用（DB操作・API呼び出し・repo外のファイル変更）を巻き戻せないため、別途の確認が必要
- **fan-out移行のpilot-first原則**: 大規模なタスクをいきなり全量で fan-out するのではなく、まず数ファイルでパイロット実行して失敗パターンを洗い出してから全体展開する
- **mise運用の罠**: ツール本体をインストールしても、グローバル設定に `[tools]` セクションがなければどのバージョンも有効化されず、PATH解決は野良の Homebrew 版が優先されたままになる。Nix側には言語ランタイムを一切入れず、mise activate を PATH の優先位置に保つ運用が二重管理事故を防ぐ
- **セッション終了時の理解度検証コマンド**: restate-first → 3階層理解(problem/solution/broader-context) → why深掘り → クイズ、の順で人間の理解を検証する軽量コマンド。`/goal` 相当のhard gateはデフォルトoff、`--strict`でopt-inする設計が摩擦を抑える

## 実践的な適用

dotfiles では Ghostty + cmux + aerospace の3層構成。cmux を `workspace 4` に固定し AI coding terminal と役割明記。`/dispatch` スキルが cmux Worker を起動する際は `new-workspace → send → send-key enter → read-screen --scrollback → close-surface` のパターンを踏む。tmux はリモート SSH 専用に位置づけ直し、ローカルでの多重化は cmux に統一している。`cmux-notify.sh` が Stop/Notification hook で cmux notify + claude-hook notification を担う。信頼性ラダーと信頼ティアは `references/cli-discovery.md` に、mise 運用ルールは `.config/mise/config.toml` に実装されている。`scripts/runtime/launch-worker.sh` は cmux surface がグローバル採番であるため `list-pane-surfaces` で実 surface ref を動的解決するよう修正済み（固定 `surface:1` 前提のバグを解消）。

## 関連概念

- [claude-code-architecture](claude-code-architecture.md) — Claude Code の内部アーキテクチャとエージェント連携
- [workflow-optimization](workflow-optimization.md) — マルチエージェント並列実行とワークフロー最適化

## ソース

- [cmux エコシステム分析](../../research/2026-03-22-cmux-ecosystem-claude-code-analysis.md) — 5コンポーネントとワークスペース分離アーキテクチャ
- [Ghostty SAND / cmux 調査](../../research/2026-03-22-ghostty-sand-cmux-analysis.md) — SAND キーバインドと cmux 通知統合
- [デュアルオーディエンス CLI 分析](../../research/2026-04-02-dual-audience-cli-analysis.md) — 人間とエージェントの双方に対応する CLI 設計原則
- [The New Software: CLI, Skills & Vertical Models](../../research/2026-04-11-new-software-cli-skills-vertical-models-analysis.md) — SaaS戦略記事からcascade gate採用、vertical modelは対象外
- [Boris の30 Tips完全版](../../research/2026-04-30-boris-30tips-absorb-analysis.md) — Boris 30 Tipsを分析、hook監視等4件を既存に軽量追記
- [cmux カスタマイズ調査メモ](../../research/2026-05-15-cmux-customization-notes.md) — cmux全設定を網羅調査、方針決定は次セッションに持ち越し
- [My Agent Stack For Automating My Personal Life](../../research/2026-05-31-personal-agent-stack-absorb-analysis.md) — 個人生活自動化記事を分析、ツール信頼性ラダーと操作信頼ティアの2軸を採用
- [Suzanne teach-back prompt](../../research/2026-06-02-suzanne-teachback-absorb-analysis.md) — Suzanne teach-backを分析、軽量/teachbackコマンド採用
- [私の最強のMac開発環境2026 (Nix+mise)](../../research/2026-06-02-typhoon-nix-mise-absorb-analysis.md) — Nix+mise記事を検証、mise未活用のランタイム二重管理事故を発見し統合
