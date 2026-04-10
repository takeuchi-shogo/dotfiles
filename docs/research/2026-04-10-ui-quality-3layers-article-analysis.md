# Claude Code の SKILL.md に「品質3層定義」を書いたら、40画面のデザインが破綻しなくなった — 分析レポート

## Meta

| 項目 | 内容 |
|------|------|
| タイトル | Claude Code の SKILL.md に「品質3層定義」を書いたら、40画面のデザインが破綻しなくなった |
| 著者 | UIデザインスタジオ代表（AIで Figma デザインを 1 年以上運用） |
| 種別 | ブログ記事 |
| 取り込み日 | 2026-04-10 |
| ステータス | integrated (パイロット実行中) |

---

## Summary

40画面以上のデザインをAIと協業で進めると「1画面は完璧だが全体が破綻する」という問題が繰り返し起きた。原因は品質水準の定義がなく、AIがすべての画面を同一基準で最大品質化しようとすること。解決策として SKILL.md に品質の3層定義（L1 機能品質 / L2 体験品質 / L3 感動品質）を埋め込み、配分を事前に決定（L1=52%/L2=36%/L3=12%）した。Wave 方式（全体浅く→中程度→深く）と組み合わせることで、42画面のデザインプロジェクトを破綻させずに完走できた。

記事の本質（Codex 指摘）は手法の表層ではない。「配分を先に固定することで局所最適化の誘惑を封じる」という構造的アプローチにある。1画面完璧主義が全体破綻につながる因果を、事前の制約設定で断ち切る。

---

## Phase 1: Extraction

### 手法の構造化抽出

| # | 手法 | 概要 |
|---|------|------|
| 1 | 品質の L1/L2/L3 層定義 | L1=機能品質（全画面必須）、L2=体験品質（主要画面）、L3=感動品質（特定画面集中） |
| 2 | Wave 方式 | 全体浅く → 中程度 → 深く。1画面ずつ完璧にしない |
| 3 | 品質配分の事前決定 | 42画面例: L1=52%/L2=36%/L3=12% を着手前に確定 |
| 4 | AI分業の品質層階層化 | L1=AI主導 / L2=AI+人間協業 / L3=人間主導 |
| 5 | SKILL.md 検証基準埋め込み | L1 チェック項目を生成中に照合できる形で記述（コンポーネント準拠、トークン参照、Auto Layout、命名規則、5状態定義） |

### L1 必須項目（記事の具体例）

- コンポーネントライブラリ準拠
- デザイントークン参照（ハードコード禁止）
- Auto Layout 適用
- 命名規則遵守
- 5状態定義（通常/ホバー/フォーカス/エラー/ディスエーブル）

---

## Phase 2: Gap Analysis

| # | 手法 | 判定 | 理由 |
|---|------|------|------|
| 1 | 品質の L1/L2/L3 層定義 | Gap | 評価軸（defense-matrix 5層、design-reviewer 4次元）は適用義務の層定義を代替しない。「何を評価するか」と「どの画面にどの水準を義務付けるか」は別問題 |
| 2 | Wave 方式 | Partial | experiment-discipline の Wave は仮説検証用途。実装フェーズの「全体→詳細」反復とは問題設定が違う |
| 3 | 品質配分の事前決定 | Gap | S/M/L 規模はサイズ見積で、品質層別コスト配分とは別物。事前確定ロジックなし |
| 4 | AI分業の品質層階層化 | N/A（取り込まない） | 既存の速度軸・脅威軸・ロール軸の分業で十分。品質層軸の転用は筋が悪い。可逆性・爆発半径・検証容易性の観点で価値なし |
| 5 | SKILL.md 検証基準埋め込み | Gap | Atomic Skill の Independent Evaluability 要件はあるが「参考資料」レベルで、「生成中に照合」されない |
| 6 | frontend-design/ui-ux-pro-max の品質軸 | Partial | 10 Rule Categories + pre-delivery-checklist あり。全画面一律 flat で差別配分は未実装 |
| 7 | 画面ごとの配分判断ロジック | Gap | Refine Operation 5種あるが事前配分決定ロジックなし |

---

## Phase 2.5: Refine（Codex + Gemini 批評と統合）

### Codex 批評の主要指摘

Codex は当初の Pass 1 判定を複数修正した。

- **K1 Partial → Gap**: 「粒度違い」で済ませるのは弱い。評価軸の存在は適用義務の差の事前決定を代替しない。Gap に格上げ
- **K2 Already → Partial**: experiment Wave と delivery Wave は問題設定が違う。混同は危険
- **K4 Partial → N/A（取り込まない）**: AI 分業の新軸追加は可逆性・爆発半径・検証容易性で切るべき。既存軸で十分
- **K5 Partial → Gap**: 「SKILL.md に書いてある」と「生成中に照合できる」は別物。最も重要な修正
- **K6 Already → Partial**: flat 運用で差別配分が未実装。Already は過剰評価
- **L3「感動品質」はハーネスでは不要**: 抽象的な Must は形骸化する。ハーネスに持ち込まない
- **52/36/12 固定比率は偽精密**: rough budget（Must/Important/Optional 程度）で十分
- **取り込み優先度 TOP3**: K5（最優先）> K2 > K1 縮約版

### Gemini 補完の主要知見（推測を含む）

> 注意: Gemini CLI が内部エラーで Google Search grounding は失敗。以下は Gemini の知識ベースからの推測を含む。

- **Kano モデルとの対応（推測）**: L1/L2/L3 は Kano モデルの必須品質/一次品質/魅力品質と概念的に近い。ただし dotfiles での運用とは独立した学術的文脈
- **Wave の性格（推測）**: 記事の Wave は Iterative Deepening より Progressive Enhancement に近い
- **先行事例**: Constitutional AI（arXiv:2212.04037）が「SKILL.md に基準埋め込み」のアカデミックな先行事例と見なせる
- **未言及トレードオフ（推測）**: L1/L2 境界の曖昧さ、昇格コスト、%変動耐性、小規模プロジェクトへのオーバーヘッド
- **dotfiles 固有リスク（推測）**: dotfiles は「モジュール単位の完全性」を重視する設計であり、Wave 方式の「全体浅く」が機能しない可能性。パイロット検証が必須

---

## Phase 3: Triage

選択基準: 可逆性・爆発半径・検証容易性・既存設計との整合性。

| # | 手法 | 採否 | 根拠 |
|---|------|------|------|
| K5 | SKILL.md 検証基準埋め込み | **取り込む** | 最優先。「書いてある」→「照合できる」へ。Independent Evaluability の実質化 |
| K1 縮約版 | Must/Important/Optional 義務差 | **取り込む** | L1/L2/L3 の厳密な比率ではなく、義務付けの差（Must/Important/Optional）として導入 |
| K2 | Wave 方式 | **取り込まない** | dotfiles の設計哲学と問題設定が合わない。パイロット検証のコストに見合わない |
| K3 | 品質配分の事前決定（数値） | **取り込まない** | 偽精密。rough budget（Must/Important/Optional）で代替 |
| K4 | AI分業の品質層階層化 | **取り込まない** | 既存軸で十分。新軸追加は管理コスト増 |
| K6 | 差別配分の実装 | **取り込まない** | K5+K1 で代替可能 |
| K7 | 事前配分判断ロジック | **取り込まない** | K5+K1 の範囲外。スコープ外 |

**実行規模: パイロット先行**

---

## Phase 4: Integration Plan

### 変更ファイル一覧

| # | ファイル | 変更内容 |
|---|---------|---------|
| 1 | `.config/claude/skills/skill-creator/instructions/skill-writing-guide.md` | Pre-generation Contract Pattern セクション追加 |
| 2 | `.config/claude/commands/rpi.md` | Phase 1/2/3 に Must/Important Contract 追加 |

### T1: skill-writing-guide.md への追加

"Atomic Skill Design Principles" の直後に **Pre-generation Contract Pattern** セクションを挿入する。

内容:
- Must/Important/Optional の3層定義（義務付けの差）
- Good 例（生成中に照合できる具体的チェック項目）と Bad 例（設計参考止まりの抽象的記述）
- アンチパターン: 抽象的項目（「UX が良い」など）、L3 感動品質相当の Must、Must 6個超、Optional 肥大化

### T2: rpi.md への追加

各 Phase（Research / Plan / Implement）に Must Contract と Important Contract を埋め込む。

- **Must Contract (4項目)**: 生成中に照合される最低限の品質基準。skip 不可
- **Important Contract (3項目)**: 主要ステップで確認する。明示的 skip は許容するが記録必須
- L3「感動品質」相当（抽象的・主観的）の項目は意図的に排除

---

## Pilot Protocol

### 観測項目

| 種別 | 項目 | 方法 |
|------|------|------|
| 主観 | /rpi 使用時の判断迷いの度合い（1-5 スケール） | 記憶ベース、セッション後に記録 |
| 客観 | /rpi 後のレビュー指摘数 | レビューコメント数をカウント |
| 客観 | 手戻り回数 | 実装→修正サイクル数 |
| 客観 | verification-before-completion 違反数 | hook ログ |

### 撤退条件

次回から /rpi を 3 回使用後:

- 効果不明 or オーバーヘッドが逆効果 → `git revert` で rollback
- Must 項目が形骸化（skip される） → 項目の見直し（削減・具体化）

### 昇格条件

以下の両方を満たす場合に昇格を検討:

- 判断迷いが明確に減る（主観スコア +1 以上）
- オーバーヘッドが軽微（1 セッションあたり追加 5 分未満）

昇格先: /review, /epd へ同パターン展開を検討。

### パイロット期間

次回 /rpi 使用開始 〜 3 回完了後に評価。

---

## Implemented Changes

| ファイル | 変更サマリ | ステータス |
|---------|-----------|-----------|
| `.config/claude/skills/skill-creator/instructions/skill-writing-guide.md` | Pre-generation Contract Pattern セクション追加（Must/Important/Optional 3層定義、Good/Bad 例、アンチパターン） | ✅ 実装済み |
| `.config/claude/commands/rpi.md` | Phase 1/2/3 に Must Contract (4項目) + Important Contract (3項目) 追加。L3 感動品質相当を意図的排除 | ✅ 実装済み |
| `docs/research/2026-04-10-ui-quality-3layers-article-analysis.md` | 本レポート | ✅ |
