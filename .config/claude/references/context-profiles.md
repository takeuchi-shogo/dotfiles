---
status: reference
last_reviewed: 2026-04-23
---

# Context Profiles

## プロファイル定義

| プロファイル | 用途                 | learnings フィルタ                                       |
| ------------ | -------------------- | -------------------------------------------------------- |
| `default`    | 通常の開発作業       | importance >= 0.4, 上位5件                               |
| `planning`   | 設計・アーキテクチャ | type: decision/pattern 優先, 上位8件                     |
| `debugging`  | バグ修正・調査       | type: error/correction 優先, importance >= 0.3, 上位10件 |
| `incident`   | 障害対応・緊急       | 直近24h の全 learnings, 時系列優先                       |

## 自動判別キーワード

### planning

- 設計, アーキテクチャ, architecture, design, plan, 構成
- どうする, どうすべき, 方針, 戦略, strategy
- 新機能, feature, リファクタ

### debugging

- バグ, bug, エラー, error, 失敗, fail
- 動かない, 壊れ, broken, crash
- なぜ, why, 原因, cause, 調査

### incident

- 障害, incident, 緊急, urgent, 本番, production
- ダウン, down, 止まっ, 復旧

## 手動オーバーライド

プロンプトに `@planning` `@debugging` `@incident` を含めると自動判別を上書き。
