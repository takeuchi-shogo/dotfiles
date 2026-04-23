---
status: reference
last_reviewed: 2026-04-23
---

# Adversarial Evaluation Criteria

> design-reviewer の 4 次元主観的品質評価を Code/API/Documentation に拡張。
> 各ドメインは 4 次元で評価し、AI Anti-Pattern（AI Slop）リストで品質劣化を検出する。

---

## Code Quality（コード品質）

| 次元 | Weight | 定義 |
|------|--------|------|
| Clarity | High | 意図が読み取れるか。命名、構造、フロー |
| Correctness | High | ロジックが正しいか。エッジケース、nil 安全性 |
| Efficiency | Standard | 不要な計算・I/O がないか |
| Maintainability | Standard | 変更容易性。結合度、凝集度 |

### Code AI Anti-Patterns
- 過剰な try-catch（エラーの握り潰し）
- 意味のないコメント（コードの 1:1 繰り返し）
- 不要な抽象化（1回しか使わないヘルパー関数）
- 防御的すぎるバリデーション（内部コードへの不要なチェック）
- 過剰な型アノテーション（自明な型への冗長な注釈）

## API Design（API 設計）

| 次元 | Weight | 定義 |
|------|--------|------|
| Consistency | High | 命名規則、パラメータ順序、レスポンス形式の統一 |
| Discoverability | High | 使い方が推測可能か。ドキュメントなしで使えるか |
| Safety | Standard | 不正入力への耐性。型安全性 |
| Extensibility | Standard | 後方互換を保ちつつ拡張可能か |

### API AI Anti-Patterns
- REST 規約無視（動詞を URL に含む、HTTP メソッドの誤用）
- 一貫性のないエラー形式（エンドポイントごとにエラー構造が異なる）
- 過剰なネスト（3 階層以上のレスポンスネスト）
- 過剰な汎用化（全てを受け入れる any 型パラメータ）
- ドキュメントとの乖離（スキーマ定義と実際のレスポンスが不一致）

## Documentation Quality（ドキュメント品質）

| 次元 | Weight | 定義 |
|------|--------|------|
| Accuracy | Critical | コードの現状と一致しているか |
| Completeness | High | 必要な情報が漏れていないか |
| Freshness | Standard | 最終更新が妥当か。陳腐化していないか |
| Navigability | Standard | 必要な情報に素早く到達できるか |

### Documentation AI Anti-Patterns
- コードの 1:1 転記（ソースをそのまま自然言語に変換しただけ）
- 陳腐化した例（動かないサンプルコード）
- 実装詳細の繰り返し（同じ説明が複数箇所に散在）
- 過剰な導入文（本題に入るまでの冗長な前置き）
- 「詳細は〜を参照」の連鎖（参照先がさらに別の参照先を指す）

---

## Design Quality（デザイン品質）— 既存

design-reviewer が使用する 4 次元評価は別途定義済み:
- Design Quality (重) / Originality (重) / Craft (軽) / Functionality (軽)
- 詳細: design-reviewer エージェント定義を参照

---

## 採点ガイド

各次元は 1-5 で採点:
- **5**: 優れている — 模範的で学習対象にできるレベル
- **4**: 良好 — 明確な問題なし
- **3**: 許容範囲 — 軽微な改善の余地あり
- **2**: 要改善 — 明確な問題がある
- **1**: 重大な問題 — 即座に対処が必要

Weight による判定: Critical 次元が 2 以下 → BLOCK、High 次元が 2 以下 → NEEDS_FIX、Standard 次元が 2 以下 → Watch

## Usage

- `/review` の Step 3 (Dispatch) で reviewer プロンプトに評価基準を注入
- `/autonomous` の QA Phase で Evaluator Agent がこの基準で採点
- `adversarial-evaluation-criteria.md` として参照
