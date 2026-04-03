---
source: https://www.aihero.dev/my-grill-me-skill-has-gone-viral
date: 2026-04-03
status: integrated
---

## Source Summary

Matt Pocock の「grill-me」スキルがバイラルに広まった事例。シンプルなプロンプト1つで
プラン・設計のストレステストを行う手法。

- **主張**: 容赦ない逐次インタビューがプランの穴を事前に潰す最もコスト効率の良い方法
- **手法**: 決定木走破、AI推奨回答の提示、1問ずつ逐次質問、コードベース探索優先
- **根拠**: バイラルに広まった実績、45分セッションで深い共有理解に到達
- **前提**: ストレステスト対象のプラン・設計が存在すること

## Gap Analysis

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | 容赦ない逐次質問 | Partial | `/interview` は spec 策定目的、`/think` は反論・盲点寄り |
| 2 | 決定木走破 | Gap | 明示的な決定木プロトコルなし |
| 3 | AI推奨回答の提示 | Gap | 選択肢提示はあるが推奨案の明示ルールなし |
| 4 | コードベース探索優先 | Already (強化不要) | 既存スキルで同様の動作 |

## Integration Decisions

- [採用] #1-3 を統合し `/grill-interview` スキルを新設
- `/interview`（spec 策定）・`/challenge grill`（事後レビュー）との棲み分けを明確化
- #4 は既存で十分

## Plan

- `.config/claude/skills/grill-interview/SKILL.md` を新設 → 完了
