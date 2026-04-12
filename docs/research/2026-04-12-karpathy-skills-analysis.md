# Andrej Karpathy Skills — 分析レポート

- **日付**: 2026-04-12
- **ソース**: https://github.com/forrestchang/andrej-karpathy-skills
- **フレームワーク**: LLM の3つの系統的エラー（暗黙的仮定・過度な複雑化・無関係な変更）を防ぐ4原則

## 記事の主張

LLM は以下のエラーを系統的に繰り返す:
- **Silent assumptions**: 暗黙の仮定で実装方針を決める
- **Over-engineering**: Strategy pattern 等で不要に複雑化
- **Scope creep in diffs**: バグ修正時にスタイル変更等の無関係な変更を混入

対策として4原則を提唱:
1. **Think Before Coding** — 不確実性→停止→複数解釈提示→選択
2. **Simplicity First** — 要求以上の機能を書かない、YAGNI
3. **Surgical Changes** — タスク無関係な改善・フォーマット変更をしない
4. **Goal-Driven Execution** — テスト駆動の段階的検証ループ

## ギャップ分析結果

### Gap / Partial

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | 多解釈の構造的列挙プロトコル | Partial | overconfidence-prevention.md に「選択肢を提示して聞く」はあるが構造的列挙プロトコル欠如 |
| 3 | スコープ外変更の3層禁止 | Partial | Scope Discipline あるがコード/依存/設計の3層明示なし |
| 5 | 過度な抽象化の具体アンチパターン | Partial | 1回ヘルパー禁止あるが具体的パターン名と対比例不足 |
| 6 | diff 汚染の micro-level ルール | 低 Partial | hook 体系が暗黙カバー。明示ルール不在だが実効性は高い |

### Already

| # | 項目 | 判定 |
|---|------|------|
| 2 | YAGNI | 強化不要 |
| 4 | TDD 検証ループ | 強化可能 — 事前宣言→比較ループ欠如 |
| 7 | 認知的透明性 | 強化不要 |

## セカンドオピニオン

### Codex 批評
- 分析は instruction 層のみで判定しており、hook/gate の多層防御を考慮不足
- 真のギャップは hook で検出しにくい #1（暗黙的仮定の検知）と #5（抽象化スロップの具体例）
- #4 TDD は「期待される変化の事前宣言」が欠如しており強化すべき
- #6 は Lefthook + formatter が暗黙的にカバー、低優先度に格下げ

### Gemini リサーチ
- GitHub で 3,500+ Star、多数の .cursorrules / CLAUDE.md に組み込み済み
- Think Before Coding の分析麻痺リスク（タイムボックスが必要）
- Surgical Changes の断片化リスク（局所最適の繰り返しでアーキテクチャ劣化）
- SDD（Specification Driven Development）が 2026年の代替フレームワークとして台頭

## 取り込み内容

全 Gap/Partial (#1, #3, #5, #6) + Already 強化 (#4) の5項目を選択。

### 変更リスト

| 対象ファイル | 変更内容 |
|-------------|---------|
| `rules/common/overconfidence-prevention.md` | 多解釈の構造的列挙プロトコル（Interpretation A/B/C 形式 + 分析麻痺防止ガード） |
| `rules/common/code-quality.md` | スコープ外変更の3層禁止テーブル（コード/依存/設計） |
| `rules/common/code-quality.md` | 過度な抽象化アンチパターン（Strategy pattern の NG/OK 例 + 判断基準） |
| `references/workflow-guide.md` | Verify の強化ルール（Act 前の事前宣言 + Verify での突き合わせ） |

合計: 3ファイル、55行追加、1行修正
