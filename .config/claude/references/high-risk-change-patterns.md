---
status: reference
last_reviewed: 2026-04-23
---

# High-Risk Change Patterns

> 高リスク変更のパターン定義。PostToolUse hook (`change-surface-advisor.py`) が参照し、
> edge-case-hunter / silent-failure-hunter の自動起動をアドバイスする。

## リスクレベル定義

| レベル | 意味 | アクション |
|--------|------|-----------|
| **Critical** | データ損失・セキュリティ侵害の可能性 | red-team brief 必須を強く推奨 |
| **High** | 機能障害・パフォーマンス劣化の可能性 | edge-case-hunter 推奨 |
| **Medium** | silent failure の可能性 | silent-failure-hunter 推奨 |

## パターン一覧

### Critical

| パターン | ファイル例 | リスク | 推奨エージェント |
|---------|-----------|--------|----------------|
| 認証ロジック変更 | `auth.go`, `middleware/jwt.go` | 認可バイパス | edge-case-hunter + security-reviewer |
| DB スキーマ変更 | `*.sql`, `migration/*.go` | データ損失、後方互換性破壊 | migration-guard |
| Hook・Policy 変更 | `scripts/policy/*.py`, `settings.json` | ハーネス無効化 | harness contract 準拠確認 |
| 暗号・署名処理 | `crypto*`, `sign*`, `hash*` | セキュリティ脆弱性 | security-reviewer |

### High

| パターン | ファイル例 | リスク | 推奨エージェント |
|---------|-----------|--------|----------------|
| 外部 API クライアント | `*_client.go`, `api/external*` | タイムアウト、リトライ不備 | edge-case-hunter |
| 並行処理 | `*worker*`, `*channel*`, `sync*` | デッドロック、race condition | edge-case-hunter |
| キャッシュロジック | `cache*`, `*_cache*` | 一貫性違反、stale data | edge-case-hunter |
| Rate limiting | `rate*`, `throttle*`, `limiter*` | DoS 耐性 | edge-case-hunter |

### Medium

| パターン | ファイル例 | リスク | 推奨エージェント |
|---------|-----------|--------|----------------|
| 設定・環境変数 | `config*`, `.env*` | デフォルト値の安全性 | silent-failure-hunter |
| エラーハンドリング | `error*`, `*_error*` | エラー握り潰し | silent-failure-hunter |
| ログ・計装 | `logger*`, `telemetry*` | 観測可能性の欠落 | silent-failure-hunter |
| バリデーション | `valid*`, `sanitiz*` | 入力検証の抜け穴 | edge-case-hunter |

## Load-Bearing Judgment

ファイル拡張子・命名 pattern では捕捉しきれない、**「何が load-bearing か」の判断**を要するケース。
hook 化はしない (approval fatigue 回避、ADR-0006 Human Judgment 分類)。instruction として参照する。

### Load-bearing の定義

以下のいずれかに該当する code/構造/設定:

- **複数の hook/skill/agent から参照される**: 削除・変更で連鎖破壊する
- **暗黙の不変条件を担保している**: 型・スキーマ・契約として明示されていないが、依存元が前提にしている
- **過去の失敗を防ぐために存在する**: 削除すると過去のバグが再発する (commit log に "fix: ..." と紐づく)
- **観測可能性の起点**: ここを通る信号で他の hook/gate が判断している

### 触る前の確認手順

1. **影響範囲を grep で数える**:
   ```bash
   rg -l "<symbol or path>" .config .codex .cursor docs scripts
   ```
2. **3 件以上の参照があれば user 確認推奨** (S 規模でも plan を一度立てる)
3. **commit log で変更理由を確認**: `git log --oneline -- <file>` で「fix:」や「revert:」の存在を確認
4. **削除する場合は 30 日 staleness 評価**: `references/harness-stability.md` の手順に従う

### Anti-Patterns

- ❌ 「未使用に見えるから消す」→ 別 hook が間接的に参照している可能性
- ❌ 「regex で警告すれば十分」→ load-bearing 判定は文脈依存、false positive 多発
- ❌ 「hook 化して block する」→ 判断を奪うと開発が止まる、approval fatigue で形骸化

### 由来

「How I got banned from GitHub due to my harness pipeline」(2026-04) — pipeline 内の load-bearing chunker を最適化目的で消し、attestation が崩壊した事例の翻訳。
hook 化判断は ADR-0006 を参照。
