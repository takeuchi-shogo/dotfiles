---
description: "Spec のための深いインタビューを実行する"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Agent, AskUserQuestion
skills: [spec]
---

# /interview

AskUserQuestionTool を使った深いインタビューで spec を策定する: $ARGUMENTS

spec スキルの Deep Interview Protocol に従って実行する。

1. 引数あり（spec ファイルパス）: 既存の spec を読み込み、深掘りインタビュー
2. 引数あり（アイデア）: アイデアを元に深掘りインタビュー → spec 生成
3. 引数なし: アイデアを聞いてからインタビュー開始

完了後、spec ファイルを保存し Session Handoff ガイダンスを出力する。
