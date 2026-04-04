# Letta AI: "Why Memory Isn't a Plugin (It's the Harness)" — Analysis

- **source**: Letta AI (MemGPT) "Why memory isn't a plugin (it's the harness)"
- **date**: 2026-04-04
- **status**: integrated

---

## Source Summary

Letta AI (MemGPT) の投稿。メモリ管理はプラグインではなくハーネスの中核責任であるという主張。エージェントのコンテキスト管理（何をロードするか、何が圧縮を生き残るか、何を永続化するか）は不可視の意思決定であり、外部に委譲すべきではない。

主張:
- メモリはハーネスそのもの。プラグインとして外出しすると制御を失う
- Proactive > Reactive: 消失を検知してから対処するのではなく、消失前に退避する
- 4分類（Working/Procedural/Episodic/Semantic）で保存先を決定する
- compaction survival priorities を明示的に定義する

手法:
- **Context Constitution**: メモリ管理の原則を憲法として明文化
- **PreCompact flush**: 圧縮前に key decisions をメモリにフラッシュ
- **PostCompact verification**: 圧縮後の状態検証と Plan re-grounding
- **Memory gardening**: セッション中に定期的にメモリ整理を促す
- **Cheapest Layer First**: 安い層が高い層の発動を防ぐ

---

## Gap Analysis

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | メモリ管理の原則体系 | Partial | 複数の policy ファイルに分散、統合的な原則文書なし |
| 2 | PreCompact memory flush | Partial | pre-compact-save.js は存在するが compaction 回数ベースのリマインダーなし |
| 3 | PostCompact verification | Gap | echo でログ記録のみ、検証ロジックなし |
| 4 | Memory gardening | Gap | セッション中のメモリ整理プロンプトなし |
| 5 | 4分類保存先ガイド | Already | memory-safety-policy.md に類似の分類あり |

### Already 項目の強化分析

| # | 既存の仕組み | 記事が示す弱点 | 強化案 |
|---|-------------|---------------|--------|
| 5 | memory-safety-policy.md | Working/Procedural/Episodic/Semantic の明示的分類 | 強化: context-constitution に統合して可視化 |

---

## Integration Decisions

全4項目を統合:

1. `references/context-constitution.md` を新規作成 — 7原則 + 7層要約 + ポリシーファイルへのポインタ
2. `pre-compact-save.js` に memory flush reminder 追加 — compaction 2回目以降で発動
3. `scripts/runtime/post-compact-verify.js` を新規作成 — Plan re-grounding + memory gardening + session health
4. `settings.json` の PostCompact hook を更新

---

## Plan

- [x] Task 1: Context Constitution 作成 — `references/context-constitution.md`
- [x] Task 2: PreCompact memory flush — `pre-compact-save.js` 強化
- [x] Task 3: PostCompact verification hook — `post-compact-verify.js` + `settings.json`
- [x] Task 4: Memory gardening — Task 3 に統合
- [x] Task 5: 分析レポート + `MEMORY.md` 更新
