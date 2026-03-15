# ADR-0003: マルチモデルオーケストレーション

## Status

Accepted

## Context

単一モデルでは、大規模コンテキスト分析（>200K）、深い推論、
高速フォーマットなど全要件を最適にカバーできない。

## Decision

3 層のマルチモデル構成を採用する:
- **Claude Code (Opus)** — オーケストレーター、計画、レビュー統合
- **Codex CLI (gpt-5.4)** — 設計・推論・デバッグ、reasoning effort 制御
- **Gemini CLI (2.5 Pro)** — 1M コンテキスト分析、リサーチ、マルチモーダル

委譲は hook（agent-router.py, error-to-codex.py, suggest-gemini.py）で自動提案し、
ルール（rules/codex-delegation.md, rules/gemini-delegation.md）で判断基準を定義する。

## Consequences

### Positive
- 各モデルの得意領域を活用
- 大規模コードベース分析が可能（Gemini 1M）
- 深い推論が必要な場合に Codex xhigh を利用

### Negative
- 3 ツールの管理・更新コスト
- CLI ツール間の出力形式の差異
- ネットワーク依存が増加
