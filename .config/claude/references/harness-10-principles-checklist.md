# ハーネスエンジニアリング 10原則チェックリスト

> 出典: wquguru/harness-books Book 1 Ch9 + dotfiles core_principles との突き合わせ

自分のハーネスが「工程システム」として成立しているかを評価する。

---

## チェックリスト

| # | 原則 | 確認観点 | dotfiles 対応 |
|---|------|---------|---------------|
| 1 | **モデルは不安定部品** | モデル出力を無条件に信頼していないか？権限・検証・ロールバックが組み込まれているか？ | `core_principles`: 手抜きなし + 検証 |
| 2 | **Prompt は制御面** | Prompt を人格装飾ではなく行動制御として設計しているか？分層・優先度・注入条件が明確か？ | `CLAUDE.md` の `<important if>` 条件付きタグ |
| 3 | **Query Loop が心拍** | 代理システムに持続的な実行循環があるか？入力治理・ツール調度・回復分岐・停止条件を持つか？ | CC 内蔵。`completion-gate.py` で外部から補強 |
| 4 | **ツールは受管理実行** | ツール呼び出しに調度纪律があるか？高危険ツールに高密度制約があるか？ | `bashSecurity` 22種チェック + `protect-linter-config.py` |
| 5 | **コンテキストは作業メモリ** | 長期規則・持久記憶・会話連続性・臨時対話を分層治理しているか？compact 戦略があるか？ | CLAUDE.md / MEMORY.md / Session Memory 3層 + autocompact |
| 6 | **エラーパスは主パス** | prompt too long, max_output_tokens, hook 回環等を設計時に組み込んでいるか？catch で誤魔化していないか？ | `failure-taxonomy.md` + `resource-bounds.md` |
| 7 | **回復の目標は作業継続** | 截断後に続写できるか？圧縮失敗時にシステムが呼吸を回復できるか？ | autocompact circuit breaker + reactive compact |
| 8 | **マルチエージェントは不確実性の分区** | 研究・実装・検証・統合を異なる職責コンテナに分けているか？ | `subagent-delegation-guide.md` + Review Gate |
| 9 | **検証は独立** | 実装者が自己採点していないか？検証が独立段階・独立角色になっているか？ | `codex-reviewer`（外部モデル）+ `code-reviewer`（並列） |
| 10 | **チーム制度 > 個人技巧** | 分層 CLAUDE.md、明確 approval、可執行 skill、lifecycle hook、追跡可能 transcript があるか？ | 全て実装済み（agents/ + skills/ + hooks/ + scripts/） |

---

## 評価方法

各項目を 0-2 で自己評価:

| スコア | 意味 |
|--------|------|
| **0** | 未実装 or 意識していない |
| **1** | 部分的に実装 or 仕組みはあるが不十分 |
| **2** | 制度として定着し、自動で機能している |

| 合計 | 評価 |
|------|------|
| 16-20 | 工程システム — ハーネスが制御構造として機能 |
| 10-15 | 進行中 — 基盤はあるが穴がある |
| 0-9 | Demo 段階 — 個人技巧に依存 |

---

## 使い方

- **新プロジェクト初期化時**: `/init-project` 後にこのチェックリストで gaps を確認
- **定期監査**: `/improve` の一環として四半期ごとに self-assessment
- **他人のハーネス評価**: `/absorb` で外部設定を取り込む際の評価基準
