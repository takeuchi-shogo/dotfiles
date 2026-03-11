---
name: codex-session-hygiene
description: Session and runtime hygiene for Codex long-running work. Use when a task spans many turns, before compact or resume, when deciding between continuing or forking a thread, or when you need to preserve stable completion criteria across continuation.
---

# Codex Session Hygiene

長時間タスクで runtime の挙動を安定させる。

## Use Cases

- 同じ goal を複数ターンにまたいで進める
- compact / resume の前後で task を壊したくない
- `/fork` するか同じ thread を継続するか判断したい
- 途中報告と最終回答の境界を明確にしたい

## Rules

- global personality は軽く保ち、出力形式や長さは task ごとに決める
- 同じ task を継続する間は goal と completion criteria を勝手に変えない
- 途中報告では進行中、未検証、open risk を明示する
- 最終回答では完了内容、検証結果、残る gap だけを簡潔にまとめる
- 同じ問題を継続するなら同じ thread を使い、別解の探索だけを fork する
- compact / resume 前には `$codex-checkpoint-resume` で filesystem checkpoint を残す

## Thread Choice

- 同じ goal、同じ completion criteria:
  - 同じ thread を継続する
- 同じ goal だが別アプローチを試したい:
  - fork する
- goal 自体が変わった:
  - 新しい task として扱う

## Before Resume

1. `tmp/codex-state/latest-checkpoint.md` を読む。
2. `Goal` と `Completion Criteria` がまだ有効か確認する。
3. `git status` と focus file を見て checkpoint が stale でないか確かめる。
4. `Next Step` から再開する。
