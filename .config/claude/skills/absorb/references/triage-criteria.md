# Triage Criteria — 知見の取捨選択基準

## 判定マトリクス

|  | 適用コスト 低 | 適用コスト 高 |
|--|-------------|-------------|
| **効果 高** | 即採用 | 検討（ROI評価） |
| **効果 低** | 後回し | スキップ |

## 適用コスト評価

| コストレベル | 基準 |
|-------------|------|
| 低 | 1ファイル変更、既存パターンに沿う |
| 中 | 2-5ファイル、新パターン導入 |
| 高 | 6ファイル超、アーキテクチャ変更、hook追加 |

## 効果評価

| 効果レベル | 基準 |
|-----------|------|
| 高 | 毎日の作業に影響、エラー防止、時間短縮 |
| 中 | 週1回程度の作業に影響 |
| 低 | 稀なケースにのみ有効 |

## フィルタリングルール

1. **Already (強化不要) → スキップ**: Phase 2 Pass 2 + Phase 2.5 で強化不要と確認済みのもの
2. **Already (強化可能) → 検討**: 強化案を Step 2 で個別に選択可能
3. **N/A → スキップ**: 前提条件が合わないものは取り込まない
4. **1記事から最大5タスク**: 消化不良防止
5. **前提条件チェック**: 記事の前提と当セットアップの文脈が合うか確認（Phase 2.5 Gemini の補完情報も参照）
6. **既存の仕組みとの衝突チェック**: 新手法が既存パターンと矛盾しないか（Phase 2.5 Codex の批評も参照）

## Launch Filter (5 tests)

> 出典: "What to Learn, Build, and Skip in AI Agents (2026)" (anonymous, 2026-04)
> 個別の framework / tool / library 採用判断時に Pruning-First と併用する 5 質問。

| # | 質問 | 採用判断のヒント |
|---|------|----------------|
| 1 | **2 年後にこれは意味があるか？** | wrapper / CLI flag / "Devin for X" は No。protocol / pattern / infra は Yes 寄り。half-life で見る |
| 2 | **信頼できる engineer が production で使い、正直な postmortem を書いているか？** | marketing post は信号にならない。"we tried X and here's what broke" 系 blog のみ採用根拠 |
| 3 | **採用すると既存の tracing / retries / config / auth を捨てる必要があるか？** | Yes なら frameworks-trying-to-be-platforms。production 死亡率 90%。No なら primitive 寄り |
| 4 | **6 ヶ月 skip するコストは何か？** | 多くの場合 nothing。**機会費用観点** — skip しても情報量が増えるだけで競争劣位にはならない。Pruning-First の根拠になる |
| 5 | **これが実際に agents を改善するかを measure できるか？** | No なら vibes 採用。eval を持っていれば data に決めさせられる |

### 6-month signal habit

新しい launch を見たら、「6 ヶ月後に何が見えればこれが重要だったと信じるか」をその場で書き留める。
6 ヶ月後にチェックバックすれば、大半は問いが自分で回答済みで、注意は compound する primitive に温存できる。

### 実運用での位置づけ

- /absorb workflow 自体への適用: 記事や launch announcement を Phase 1 で抽出する際、test 1-2 を見てから extraction 深度を決める (postmortem ベースの記事は深掘り、marketing post は表層抽出のみ)
- test 4 (skip cost) は **N/A 判定の補強根拠** として使う ("6 ヶ月後に再評価で十分" は明示的 N/A 理由)
- test 5 (measurable) は AutoEvolve の signal が観測可能かと連動 (friction-events.jsonl で見えない改善は採用根拠が弱い)
