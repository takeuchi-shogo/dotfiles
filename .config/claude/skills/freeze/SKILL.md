---
name: freeze
description: >
  Use when debugging or investigating — prevents accidental file modifications.
  Prompts for confirmation on every Edit/Write so you only add logs, not 'fix' unrelated code.
  Triggers: 'freeze', '編集禁止', 'デバッグモード', 'read-only mode', '修正しないで'.
  Do NOT use for: normal development or review (use /review which has its own Edit guard).
origin: self
metadata:
  pattern: guard
hooks:
  PreToolUse:
    - matcher: "Edit|Write"
      hooks:
        - type: prompt
          prompt: >
            [FREEZE MODE] ファイル編集がブロックされています。
            デバッグ中はログ追加・調査のみ行い、コードの「修正」は行わないでください。
            このファイル編集は本当に必要ですか？（ログ追加やデバッグ出力のみ許可）
---

# /freeze — ファイル編集フリーズモード

デバッグ・調査中にコードを「つい直してしまう」のを防ぐ安全装置。
スキル起動中は **Edit/Write ツール** に対して確認プロンプトが表示されます。

## Usage

```
/freeze
```

## When to Use

- バグ調査中に「ついでに直す」を防ぎたいとき
- 他人のコードを読んでいる最中に誤編集を防ぎたいとき
- ログ追加だけ許可して本体コードは触らせたくないとき
- 複雑なデバッグで原因特定前に修正を始めてしまうのを防ぐとき

## How It Works

PreToolUse フックで Edit/Write ツール呼び出しをインターセプトし、
本当に必要な編集かどうかを確認します。

Read, Grep, Glob, Bash(読み取り系) はブロックしません。

## Gotchas

- **hard block ではない・スコープ指定もできない**: `type: prompt` なので「はい」で通る。ディレクトリスコープがないため「対象領域の外だけ止める」使い方はできず、全 Edit/Write に確認が入る
- **ログ追加は許可**: デバッグ用の console.log/print 追加は「はい」で通す
- **Bash での echo リダイレクトは対象外**: `echo "debug" >> file` は Bash 経由なのでブロックされない
- **review スキルとの併用不可**: /review も Edit/Write をガードするため、両方起動すると二重確認になる
- **セッション限定**: 新セッションでは再起動が必要
