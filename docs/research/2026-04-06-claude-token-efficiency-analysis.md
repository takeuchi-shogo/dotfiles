---
source: "I stopped hitting Claude's usage limits - 10 things I changed"
date: 2026-04-06
status: integrated
---

## Source Summary

**主張**: Claude はメッセージ数ではなくトークン数をカウント。トークンを賢く使えば使用制限に達しにくくなる。

**手法** (10項目):
1. プロンプト編集→再生成（フォローアップを送らない）
2. 15-20メッセージごとに新チャット
3. 質問をバッチして1メッセージに
4. 繰り返しファイルはProjectsに
5. Memory & User Preferences設定
6. 未使用機能をオフ
7. 簡単タスクにはHaikuを使う
8. 作業を日中に分散（5hローリングウィンドウ）
9. オフピーク時間に作業（PT 5-11AM がピーク、2026/3/26〜）
10. Extra Usageをセーフティネットに

**根拠**:
- トークンコスト: Total = S × N(N+1) / 2（S=平均トークン/交換, N=メッセージ数）
- 30番目のメッセージは1番目の31倍のコスト
- 100+メッセージで98.5%が履歴再読み込みに消費（Aniket Parihar 調査）
- Haikuで50-70%のバジェット節約

**前提条件**: Claude.ai Web UI ユーザー向け。Claude Code CLI（API課金）とは課金モデルが異なる。

## Gap Analysis

### Gap / Partial / N/A

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | プロンプト編集→再生成 | N/A | CLI にメッセージ編集 UI なし |
| 2 | 15-20msg で新チャット | Already (強化不要) | Compaction Counter=3, TTL=2h, `/checkpoint` |
| 3 | 質問をバッチ | Already (強化不要) | 並列ツール呼び出し + agent delegation |
| 4 | ファイルをProjectsに | Already (強化不要) | CLAUDE.md + references/ + skills/ |
| 5 | Memory設定 | Already (強化不要) | Memory system + `/onboarding` |
| 6 | 未使用機能オフ | Partial | MCP/ツールの選択的無効化は手動 |
| 7 | Haikuで簡単タスク | Already (強化可能) | agent_delegation テーブル。定量的根拠が未記載 |
| 8 | 5hウィンドウ分散 | N/A | API課金。Web UIのローリングウィンドウは無関係 |
| 9 | オフピーク時間 | N/A | API課金。ピーク時間ペナルティはWeb UIのみ |
| 10 | Extra Usage | N/A | API課金。Web UIの超過課金機能は無関係 |

### Already 項目の強化分析

| # | 既存の仕組み | 記事の知見 | 強化判定 |
|---|-------------|-----------|----------|
| 7 | agent_delegation テーブル | O(N²) コスト増の定量データ | 強化可能: resource-bounds.md に委譲の数値的動機付けを追記 |

## Integration Decisions

- **取り込み**: #7 — resource-bounds.md に O(N²) トークンコスト増大モデルを追記
- **スキップ**: #6 Partial — CLI でのツール無効化は手動で十分（低優先度）
- **スキップ**: #1,8,9,10 — Claude.ai Web UI 固有（N/A）

## Plan

1. `resource-bounds.md` に「トークンコスト増大モデル」セクションを追加
   - O(N²) 数式と具体的な数値例
   - agent delegation への接続（委譲がコスト削減になる理由）
