# Best-of-N 並列実行ガイド

N 個の worktree で同一プロンプトを並列実行し、テスト結果を比較して最良を選択する。

## いつ使うか

- 非決定的なタスク（リファクタリング、設計、創造的なコード生成）
- 成功率が低い難しいタスク（p < 0.5）
- 複数のアプローチを比較したい場合

## いつ使わないか

- 決定的なタスク（typo 修正、1行変更）— N=1 で十分
- 共有状態を変更するタスク（DB マイグレーション、API 変更）
- 既に成功率が高いタスク（p > 0.8）

## 成功確率モデル

```
P(少なくとも1つ成功) = 1 - (1-p)^N
```

| p (1回の成功率) | N=2 | N=3 | N=4 | N=8 |
|:---:|:---:|:---:|:---:|:---:|
| 0.3 | 51% | 66% | 76% | 94% |
| 0.5 | 75% | 88% | 94% | 99.6% |
| 0.7 | 91% | 97% | 99% | 99.99% |

**推奨 N 値:**
- N=2: 高信頼タスク (p>=0.5) の品質向上
- N=3: 標準的な推奨値（コスト対効果の最適点）
- N=4: 低信頼タスク (p<0.4) や重要なタスク
- N>4: 収穫逓減。特別な理由がない限り非推奨

## 使い方

```bash
# 基本 (N=3, 自動選択)
best-of-n-runner.sh -n 3 -p "Implement feature X with tests"

# インタラクティブ選択（比較テーブルを表示して手動選択）
best-of-n-runner.sh -n 3 -p "Refactor module Y" --interactive

# 全結果を保持（cleanup しない）
best-of-n-runner.sh -n 4 -p "Design API Z" --keep-all

# 特定ディレクトリで実行
best-of-n-runner.sh -n 2 -p "Fix bug" -d /path/to/project
```

## 評価基準

| 基準 | 重み | 説明 |
|------|------|------|
| 終了コード | 40% | 正常終了 (exit 0) = 100点、異常 = 0点 |
| テスト通過率 | 40% | passed / (passed + failed) × 100 |
| 差分サイズ | 20% | 小さいほど高評価（逆正規化） |

テスト出力のパースはベストエフォート（grep ベース）。パース失敗時は test_score=0 とし、終了コードで判定する。

## 不採用候補からの学習

勝者を選んで終わりではなく、**敗者の差分パターン**も学習資産として活用する:

1. 勝者と敗者の diff を取得（worktree が残っている場合）
2. 敗者が「部分的に優れていた点」を抽出（例: 別のアルゴリズム選択、異なるエラーハンドリング）
3. 抽出した知見を session-learner.py の learnings に投入

**いつ実行するか:**
- N>=3 で敗者に明らかに異なるアプローチが含まれる場合
- 難易度の高いタスク（推定成功率 p < 0.5）の場合

> 根拠: SSD (arXiv:2604.01193) は「全サンプルから学ぶ」ことで「最良を選ぶ」より大きな改善を達成。難問ほどゲインが大

**多様性保持の定量的根拠:**
SSD では Pass@5 の改善が Pass@1 を上回る（全体: +18.1pp vs +12.9pp、Hard: +23.0pp vs +15.3pp）。これは勝者を1つ選ぶだけでなく、複数の多様な解を保持することの価値を定量的に示す。best-of-n で N≥3 を使う場合、2位以下の候補にも再利用可能なアプローチが含まれる確率が高い。

## Session-State 分離

各 worktree は独立した状態ディレクトリを持つ:

```
.claude/worktrees/bon-{id}-{i}/
└── .bon-state/
    ├── session-state/    ← CLAUDE_SESSION_STATE_DIR
    └── agent-memory/     ← AUTOEVOLVE_DATA_DIR
```

これにより以下の状態が worktree 間で干渉しない:
- checkpoint_manager (チェックポイント)
- stagnation-detector (停滞検出カウント)
- session-save/load (セッション状態)
- compaction-counter (コンパクション回数)

## Lock ファイルの扱い

`package-lock.json`, `go.sum`, `Cargo.lock` は worktree 内で **read-only** に設定される。
依存関係の変更が必要なタスクでは Best-of-N は非推奨（直列実行を使う）。

## 全失敗時の挙動

全 N 個の run が失敗した場合:
- exit code 1 で終了
- 全 worktree を保持（検査用）
- cmux-notify.sh で通知

## Candidate Diversity, Pruning, Escalation

> 出典: Pan et al. 2026 "Natural-Language Agent Harnesses" Appendix F — multi-candidate search モジュールの形式化。ただし同論文 RQ2 では高コスト低リターンだったため、適用条件を厳格化する。

同一プロンプトの N 並列（上記の基本モード）に加え、**仮説多様性**を導入して候補の質を上げる。

### Diversity（候補生成時）

各 worktree に同一プロンプトを渡すのではなく、以下の軸を変える:
- **仮説**: 問題の解釈・分解方法を変える
- **ツールルート**: 使う API やライブラリを変える
- **リスク選好**: 保守的アプローチ vs 大胆なリファクタリング

```bash
# 多様性モード（プロンプトバリエーションを自動生成）
best-of-n-runner.sh -n 3 -p "Fix bug X" --diverse
```

### Pruning（候補選定時）

N 個の結果から最良を選ぶ際:
1. **重複除去**: diff が実質同一の候補を除外
2. **支配解除去**: 全指標で他候補に劣る候補を除外
3. **比較**: テスト通過率、diff サイズ、コード品質で比較

### Escalation（全候補不十分時）

全 N 候補が不十分な場合:
- **拡大**: N を増やして再実行（上限 N=6）
- **再設計**: プロンプトや分解を根本的に変えて再実行
- **報告**: 無理に勝者を選ばず、全候補不十分と報告する

### 適用条件（厳格化）

> **高コスト注意**: Pan et al. (2026) RQ2 では multi-candidate search は最もコストが高いモジュールだった（トークン消費が Basic の 4 倍）。以下の条件を満たす場合のみ使用:

- 成功率が低い (p < 0.3) かつ重要なタスク
- 複数の根本的に異なるアプローチが存在する
- 単一 attempt の self-evolution retry で解決できなかった場合

**self-evolution retry (cap=3) を先に試し、それでも失敗した場合の最終手段として使う。**

## Multi-Objective Pareto Frontier

> 出典: Lee et al. 2026 "Meta-Harness" — 精度・コンテキスト消費の tradeoff curve 上の複数候補を維持。単一目的最適化では発見できない設計を見つける。

単一メトリクス（テスト通過率）の最大化ではなく、複数の目的を同時に最適化する。

### 評価軸

| 軸 | 説明 | 測定方法 |
|---|---|---|
| **精度** | テスト通過率 + 終了コード | 上記「評価基準」と同じ |
| **コンテキスト効率** | 消費トークン数 / タスク複雑度 | セッション統計から推定 |
| **diff サイズ** | 変更行数の少なさ | git diff --stat |

### Pareto 支配の判定

候補 A が候補 B を **Pareto 支配** する条件:
- A が全軸で B 以上、かつ少なくとも1軸で B を上回る

**Pareto frontier**: どの候補にも支配されない候補の集合。

### 実用ルール

- コンテキスト消費が 2x 以下で精度が同等（±2pp）なら frontier に含める
- frontier 上の候補が 3 個以上ある場合、コンテキスト効率が最も高いものをデフォルト選択
- `/improve` の `--evolve` でスキル候補を生成する際、frontier 上の候補を全て保持し、最終選択をユーザーに委ねる

### Best-of-N との統合（将来実装）

Pareto モードでは勝者を1つ選ばず、frontier 上の全候補を比較テーブルで表示する。
`best-of-n-runner.sh` に `--pareto` オプションを追加予定。現時点では手動で Pruning セクションの支配解除去ルールを適用する。

## Verbalized Sampling との併用

> 出典: Zhang et al. 2025 "Verbalized Sampling" (arXiv:2510.01171)。詳細: `references/verbalized-sampling-guide.md`

Best-of-N の各 worktree に **Verbalized Sampling (VS)** プロンプトを組み合わせることで、候補の多様性をさらに高められる。VS は temperature/top-p とは直交する軸で多様性を生むため、サンプリングパラメータの調整だけでは得られない質的な違いを持つ候補が生成される。

### 併用パターン

| パターン | 方法 | 効果 |
|---------|------|------|
| **VS-Multi × Best-of-N** | VS-Multi の各ターン出力を別 worktree の初期方針として使う | N を増やさずに候補の質的多様性が向上 |
| **VS-Standard × --diverse** | `--diverse` モードの仮説生成に VS-Standard を使う | 仮説の言語化により、より根本的に異なるアプローチが生成される |

### N 削減の可能性

VS により候補間の質的差異が大きくなるため、同じ多様性を得るのに必要な N を削減できる場合がある:
- VS なし N=4 ≈ VS あり N=2-3（創造的タスクでの経験則）
- ただし決定的タスクでは VS のオーバーヘッドが無駄になるため、従来通り N のみで制御する

## 関連ドキュメント

- `subagent-delegation-guide.md` §Shared File Detection Rule — session-state 共有ファイルの一覧
- `workflow-guide.md` §Best-of-N — 計画段階での並列比較（本ツールは実行段階の補完）
