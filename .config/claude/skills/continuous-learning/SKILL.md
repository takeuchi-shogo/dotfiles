---
name: continuous-learning
description: >
  Auto-detect and record reusable patterns from corrections, debugging, and repeated work.
  Triggers: user corrections ('no not that', 'instead do', 'don't do X'), recurring patterns (same fix applied 2+ times),
  new project conventions discovered during work, debugging insights worth preserving.
  Do NOT use for one-off fixes or task-specific context — use memory system instead.
allowed-tools: "Read, Bash, Grep, Glob"
metadata:
  pattern: pipeline
---

# Continuous Learning

## Trigger

以下の状況で自動的に発動する:

- ユーザーから修正フィードバックを受けた
- 同じ種類のバグを2回以上修正した
- プロジェクト固有の規約・パターンを発見した
- デバッグで有用な手順を確立した
- レビューで繰り返し指摘されるパターンを検出した
- AI 出力に対してユーザーが同種の編集を繰り返した（Diff-Distill トリガー）

## Workflow

### 1. Detect Pattern

修正・フィードバック・繰り返しを検知したら、以下を評価:

| 質問 | Yes → 記録対象 |
|------|---------------|
| 同じミスを2回以上した？ | パターンとして記録 |
| ユーザーが明示的に「覚えて」と言った？ | 即座に記録 |
| プロジェクト固有の規約を発見した？ | 規約として記録 |
| デバッグ手順が3ステップ以上？ | 手順として記録 |
| レビューで同じ指摘が2回？ | アンチパターンとして記録 |
| AI 出力を同じ方向に3回以上編集した？ | Diff-Distill 候補として記録 |

### 1.5. 帰納的に分類する（ブレストしない）

パターンの分類は、観察から帰納的に導出する。事前にカテゴリを定義しない。

- 表面的に似ていても根本原因が異なるなら分割
- 根本原因が同じなら、表現が異なってもグルーピング
- **最初に壊れた箇所に注目** — エラーはカスケードするため、根本原因を特定する

詳細な手法は `references/error-analysis-methodology.md` を参照。

### 2. Classify

記録するパターンを分類:

- **convention**: プロジェクト固有の規約（命名、ファイル配置、ツール使い方）
- **debug-pattern**: デバッグ手順・トラブルシューティング
- **anti-pattern**: 避けるべきパターン（やってしまいがちなミス）
- **tool-usage**: ツール・ライブラリの効果的な使い方
- **preference**: ユーザーの好み・ワークフロー

### 3. Record

記録先の判断:

```
MEMORY.md に追記（索引として1-2行）
  → 詳細が必要なら別ファイルに分離
    例: debug-patterns.md, conventions.md, anti-patterns.md
```

記録フォーマット:

```markdown
## [分類]: [パターン名]
- **状況**: いつ発生するか
- **対処**: 何をすべきか
- **理由**: なぜそうするか（省略可）
```

### 4. Validate Before Writing

記録前に必ず確認:

1. **重複チェック**: 既存の MEMORY.md と詳細ファイルを読み、同じ内容がないか確認
2. **正確性**: 1回の観察ではなく、複数の証拠があるか（ユーザー明示指示は除く）
3. **機密情報**: token, password, secret が含まれていないか
4. **簡潔性**: MEMORY.md は200行以内を維持

### 5. Apply

次回以降、記録したパターンを積極的に活用:

- 作業開始時に MEMORY.md を確認
- 関連パターンがあれば事前に適用
- パターンが古くなっていたら更新・削除

### 6. Trace-Based Rule Extraction (meta-agent Pattern)

`/improve` のトレース分析と連携し、失敗トレースから行動ルールを自動抽出する:

1. **入力**: `~/.claude/agent-memory/traces/` の失敗トレース（session-learner が `outcome: failure` を付与したもの）
2. **抽出**: 失敗の根本原因を「エージェントの行動ルール」として言語化する
   - NG: 「セッション X で refund を誤適用した」（特定トレースへの過学習）
   - OK: 「返金処理前にキャンセルポリシーを必ず確認する」（一般化された行動規範）
3. **検証**: 同一パターンの失敗が 2 件以上あるもののみ候補とする（Rule 36 Multi-trace Consensus）
4. **出力**: `situation-strategy-map.md` への追加候補として提示（自動マージは行わない）

根拠: meta-agent (Anthropic 2026) — LLM judge が自然言語批評を付与し、proposer がそこから行動ルールを抽出するパイプライン。corrections 主体の学習に加え、失敗トレースからの帰納的ルール抽出が改善ループを加速する。

## Anti-Patterns

- 1回しか起きていない事象を一般化して記録しない
- セッション固有の情報（現在のタスク詳細、一時的な状態）を記録しない
- CLAUDE.md の指示と矛盾する内容を記録しない
- 推測や未検証の結論を記録しない
- トレースを読む前に失敗カテゴリをブレインストーミングしない
- 表面的な類似性でグルーピングしない（根本原因で分類する）

## 記録しない基準（Do-Not-Record Criteria）

> 出典: pepabo 失敗学習ループ記事 (2026-04-11 /absorb, Codex 批評統合)。
> 「実戦で検証されたものだけ残す」思想を機械的に支えるため、記録**しない**基準を明文化する。
> 「念のため記録」は MEMORY 肥大化と「読まれないルール」の主因である。

以下のいずれかに該当する観察は **記録しない**（または記録しても昇格させない）:

| # | 基準 | 理由 | 判定例 |
|---|------|------|--------|
| DNR-1 | **一度きりで再発条件が言語化できない** | 単発事象は「原因が特定できていない」ことの婉曲表現。記録しても次回に適用できない | "このエラーが出た時は X した" (条件不明) |
| DNR-2 | **verify 行が書けない** | `lessons-learned.md` は verify 必須。主観的な教訓は検証不能で腐敗する | "なるべく気をつける" "注意する" |
| DNR-3 | **既存の rules/ 等でカバー済み** | 重複は参照コストを増やすだけ。既存の場所を強化すべき | 既に `rules/go.md` にある内容を MEMORY に追記 |
| DNR-4 | **「念のため」防衛記録** | 未発生のリスクヘッジは証拠ゼロ。YAGNI 違反 | "将来こうなるかもしれないから..." |
| DNR-5 | **フレームワークやツールのデフォルト挙動** | 現行モデル / ツールが自然に守ることは指示不要（dead weight 化する） | "git は HEAD を指す" |
| DNR-6 | **記事・論文由来の未検証知見** | 吸収 (/absorb) したままでは実戦検証ゼロ。まず実装・観察してから昇格 | "XX 論文によると..." を MEMORY にそのまま転記 |
| DNR-7 | **コンテキスト幅が狭すぎる** | 特定プロジェクト・特定ファイルにしか効かない知見は当該 agent-memory に留める | 単一 repo の特定関数名に依存した知見 |

### 実戦検証なしで昇格させない

記録することと昇格（MEMORY / rules への移動）は別物:

1. 記録は observation（観察）に過ぎない
2. **昇格は evidence（証拠）を要求する**: 異なる context で 2 回以上再発、verify PASS 継続、実測効果（20%以上改善）
3. 昇格条件は `improve-policy.md` の「昇格条件」表に従う

### 記録してから一定期間で見直す

- 記録直後の知見は「検証待ち」扱い
- 30 日以内に 1 回も参照されない記録は削除候補（dead-weight-scan-protocol.md と連動）
- 「壊れた → 直した + verify」形式以外の記録は簡素化 or 削除

参照: `references/improve-policy.md`（昇格条件・降格条件・容量管理）, `references/dead-weight-scan-protocol.md`（定期棚卸し）

## Examples

**Example 1: ユーザー修正からの学習**
```
ユーザー: 「bun を使って。npm じゃなくて」
→ 記録: preference: パッケージマネージャーは bun を使用（npm 不可）
```

**Example 2: デバッグパターンの記録**
```
Next.js の hydration mismatch を2回修正
→ 記録: debug-pattern: Next.js hydration mismatch
  - 状況: SSR と CSR の出力が異なる
  - 対処: useEffect で client-only 処理を分離、Date/Math.random を避ける
```

## Skill Assets

- パターン記録テンプレート: `templates/pattern-record.md`
- 検出シグナル一覧: `references/detection-signals.md`
