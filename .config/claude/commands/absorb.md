---
description: "外部記事・論文の知見を現在のセットアップに統合する"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Agent, AskUserQuestion, WebFetch
skills: [absorb]
---

# /absorb

外部知見を分析し、現在のセットアップに取り込む統合プランを生成する: $ARGUMENTS

absorb スキルの Workflow に従って実行する。

1. 引数あり（URL）: 記事を取得して分析開始
2. 引数あり（テキスト）: 貼り付けテキストとして分析
3. 引数なし: 何を分析するか聞く（AskUserQuestion で確認）

Phase 1 (Extract) → Phase 2 (Analyze) → Phase 3 (Triage) → Phase 4 (Plan) → Phase 5 (Handoff) の順で実行。
