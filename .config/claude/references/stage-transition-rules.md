---
status: reference
last_reviewed: 2026-04-23
---

# Stage Transition Rules

> ステージ遷移の Exit Criteria と Gate を定義する。
> completion-gate.py と hook が参照し、遷移判定に使用する。

## 1. デフォルトワークフロー（CLAUDE.md）

全タスクに適用。タスク規模 (S/M/L) でステージをスケーリング。

### パイプライン

```
Plan → [Spec/Plan Gate] → Implement → Test → [Review Gate] → Verify → [Security] → Commit
```

### Exit Criteria

| Stage | Exit Criteria | Gate | 失敗時 |
|-------|--------------|------|--------|
| **Plan** | 目標・スコープ・ステップが明確、ユーザー承認済み | Codex Spec/Plan Gate (M/L) | 修正→再レビュー |
| **Implement** | コード変更完了、lint パス | golden-check.py (GP-002〜GP-011) | GP 違反修正 |
| **Test** | 全テストパス、変更ファイルのテスト存在 | completion-gate.py テスト検証 | Implement に戻る |
| **Review** | PASS 判定 | Codex Review Gate (code-reviewer + codex-reviewer) | NEEDS_FIX→修正→再Review (max 3) |
| **Verify** | 動作確認完了、Design Rationale 記録 (L) | completion-gate.py comprehension check | Implement に戻る |
| **Security** | セキュリティ指摘なし (L のみ) | security-reviewer | Implement に戻る |
| **Commit** | 変更がステージング済み | — | — |

### 規模別スケーリング

| Stage | S | M | L |
|-------|---|---|---|
| Plan | skip | 必須 | 必須 + /check-health |
| Spec/Plan Gate | skip | 必須 | 必須 + 複数プラン比較(任意) |
| Implement | 必須 | 必須 | 必須 + 中間検証(3ステップ毎) |
| Test | skip | 必須 | 必須 |
| Review Gate | 必須 | 必須 | 必須 |
| Verify | 必須 | 必須 | 必須 + Design Rationale |
| Security | skip | skip | 必須 |

---

## 2. EPD 拡張ワークフロー

`/epd` 使用時に適用。Build フェーズ（Phase 5）でデフォルトワークフローに合流。

### パイプライン

```
Spec → Spike → Refine → Decide → Build(→デフォルトに合流) → Review → Ship
```

### Exit Criteria

| Phase | Exit Criteria | 成果物 | 失敗時 |
|-------|--------------|--------|--------|
| **1. Spec** | acceptance criteria を含む PRD 生成 | `docs/specs/{feature}.prompt.md` | 要件の曖昧さ → /interview で深掘り |
| **2. Spike** | worktree で最小実装完了、validate パス | spike-report.md | 実現不可 → Phase 4 Decide |
| **3. Refine** | Spike 結果が Spec に反映、max 3回反復 | 更新された spec + changelog | 3回未収束 → Phase 4 Decide |
| **4. Decide** | ユーザーが Proceed/Pivot/Abandon を明示 | 判断記録 | — (ユーザー判断が必須) |
| **5. Build** | デフォルトワークフローの Commit まで完了 | プロダクションコード | デフォルトの失敗ルールに従う |
| **6. Review** | 3軸レビュー PASS (eng + product + design) | レビューレポート | 修正→再レビュー (max 3) |
| **7. Ship** | コミット完了 | PR or merge | — |

---

## 3. Wave 1 統合（change-surface-advisor）

Plan/Implement ステージで `change-surface-advisor.py` が PostToolUse (Edit|Write) で自動検出・アドバイス。

| Change Surface | リスク | 対応ステージ | アドバイス |
|---------------|--------|-------------|-----------|
| 認証・認可 | Critical | Implement, Review | edge-case-hunter + security-reviewer 推奨 |
| DB Migration | Critical | Implement, Review | migration-guard 推奨 |
| Hook・Policy | Critical | Implement | harness contract 準拠確認 |
| 暗号処理 | Critical | Implement | security-reviewer 推奨 |
| 外部 API | High | Implement | edge-case-hunter 推奨 |
| 並行処理 | High | Implement | edge-case-hunter 推奨 |
| 設定・環境変数 | Medium | Implement | silent-failure-hunter 推奨 |
| エラーハンドリング | Medium | Implement | silent-failure-hunter 推奨 |

詳細なファイルパターンは `references/change-surface-preflight.md` を参照。

---

## 4. 失敗時の遷移ルール

| 失敗箇所 | 遷移先 | 条件 |
|---------|--------|------|
| Spec/Plan Gate 指摘 | Plan 修正 | Claude 自動修正 or ユーザー判断 |
| Test 失敗 | Implement | テスト出力を参照して修正 |
| Review NEEDS_FIX | Implement → 修正差分のみ再 Review | max 3回 |
| Review BLOCK | Implement → フル再 Review | max 3回 |
| 3回 PASS にならない | ユーザーエスカレーション | NEEDS_HUMAN_REVIEW |
| Verify 失敗 | Implement | 動作確認やり直し |
| Security 指摘 | Implement | 脆弱性修正 |
| EPD Spike 失敗 | Decide (Phase 4) | Proceed/Pivot/Abandon |
| EPD Refine 3回未収束 | Decide (Phase 4) | ユーザー判断 |
