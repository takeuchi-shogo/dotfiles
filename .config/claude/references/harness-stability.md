---
status: active
last_reviewed: 2026-04-23
---

# Harness Stability Policy

## 原則: 30日評価なしに捨てない

ハーネスの構成要素（hooks, skills, agents, references）を削除・置換する前に:
1. 最低 30 日の実運用データを収集する
2. dead-weight-scan.py で使用頻度を計測する
3. 代替案が同等以上の効果を発揮することを確認する

## 例外

- セキュリティ上の問題が発覚した場合: 即時削除
- 明らかに未使用 (0 invocations in 30 days): dead-weight scan で検出後に削除可

## 背景

「切り替えない」の強制は実験速度を殺す。「30日評価」が撤退条件を客観化する。
