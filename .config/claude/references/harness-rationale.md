# Harness Engineering Rationale

ハーネス設計の定量的根拠と設計分類。
なぜハーネスに投資するのかを判断する際に参照する。

Ref: Harness Engineering Best Practices 2026 (逆瀬川)

---

## Morph 22:1 比率

> 「モデル選択はパフォーマンスを 1 ポイント変える。ハーネス設計は 22 ポイント変える」
> — Morph 分析

**意味**: 同一モデルでもハーネスの違いで 22 点の性能差が生じる。
モデルをアップグレードするより、ハーネスを改善する方が ROI が高い。

**適用場面**: 新機能追加やツール選定で「より賢いモデルを使えば解決する」と
考えたとき、まずハーネス（hook, lint, test）の強化を検討する。

---

## Factory.ai カスタムリンター 4 分類

> **DEPRECATED**: 本セクションは [`lint-category-map.md`](lint-category-map.md) の7カテゴリフレームワークに移行しました。
> 新規ルール設計時は `lint-category-map.md` を参照してください。

カスタム lint ルールを設計する際の分類フレームワーク:

### 1. Grep-ability（検索可能性）
- named exports を強制
- 一貫したエラー型を強制
- 明示的な DTO を強制
- **目的**: エージェントが Grep でコードを発見できるようにする

### 2. Glob-ability（ファイル発見可能性）
- 予測可能なファイル構造を強制
- 命名規則の統一（kebab-case, PascalCase 等）
- **目的**: エージェントが Glob でファイルを確実に発見・作成・リファクタできるようにする

### 3. Architecture Boundaries（アーキテクチャ境界）
- レイヤー間 import の allowlist/denylist
- 依存方向の強制（上位 → 下位のみ）
- **目的**: 暗黙の結合を防ぎ、変更影響を限定する

### 4. Security/Privacy（セキュリティ・プライバシー）
- plaintext secrets のブロック
- 入力バリデーションの強制
- `eval` / `new Function` の禁止
- **目的**: セキュリティ脆弱性の自動防止

---

## フィードバック速度の階層

| 層 | 速度 | 実装 |
|---|---|---|
| PostToolUse | ms | auto-format.js (Biome, Oxlint, Ruff, gofmt) |
| Pre-commit | s | Lefthook (lefthook.yml) |
| CI | min | GitHub Actions (テストスイート) |
| Human Review | h | /review スキル |

**原則**: チェックを可能な限り左（速い層）に移動する。
PostToolUse で検出できるものを CI まで待たない。

---

## AI 生成コードの主要アンチパターン（OX Security/Snyk）

| パターン | 発生率 | 対策 |
|---------|--------|------|
| `any` 乱用 | 高 | GP-005 + `no-explicit-any: error` |
| コード重複 | 高 | GP-001 (共有ユーティリティ優先) |
| ゴーストファイル | 中 | GP-009 (golden-check.py) |
| コメント過多 | 90-100% | GP-010 (golden-check.py) |
| セキュリティ脆弱性 | 36-40% | gosec, eslint-plugin-security, Ruff S-rules |
