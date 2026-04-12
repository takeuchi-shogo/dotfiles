---
source: "https://zenn.dev/mikana0918/articles/7ad57493a04f88 / https://github.com/JuliusBrussee/caveman"
date: 2026-04-11
status: integrated
---

## Source Summary

**主張**:
日本語向け「genshijin（原始人）」口調プロンプト（体言止め・助詞圧縮・クッション語禁止）により出力トークンを最大80%削減できる。英語 caveman（68%削減限界）より12pt 高く、日本語の冗長構造を標的にした特化設計が差異を生む。セーフガードとして危険操作時は自動的に通常文にリバートする。

**手法**:
- 日本語 brevity ルール（体言止め・助詞圧縮・クッション語禁止）
- 禁止リスト型プロンプト（Drop: 形式 — "Drop: articles, filler, hedging, pleasantries"）
- 多段階強度レベル（Lite / Full / Ultra / Wenyan の4段階を caveman README で確認）
- SessionStart hook + `~/.claude/.caveman-active` ファイルブリッジによる状態永続化
- 3-arm 評価ハーネス（baseline / terse / skill）
- 危険操作時の自動リバート
- 入力圧縮ツール caveman-compress（~46% 削減）
- `npx skills add JuliusBrussee/caveman` による多エージェント配布

**根拠**: 実測: 1,483 → 296 トークン（80% 削減）を3つの実例で検証。caveman リポジトリ（GitHub 15.6k stars）の実装コードと 3-arm 評価ハーネス。

**前提条件**: Claude Code subscription 環境（トークン課金ではなく API コール数・コンテキスト制限が制約）。日英混在の技術応答を前提とする。

---

## Gap Analysis (Pass 1: 存在チェック)

| # | 手法 | 判定 | 詳細 |
|---|------|------|------|
| 1 | 日本語 brevity ルール（体言止め・助詞圧縮・クッション語禁止） | Gap | concise.md は14行の英語ベース肯定形のみ。日本語特化ルールなし |
| 2 | 禁止リスト型プロンプト（Drop: 形式） | Gap | 既存は肯定形（「結論+1行理由」）のみ。禁止リスト構文なし |
| 3 | 5段階強度レベル → 3段階に縮小 | Gap（縮小版） | output-mode 4モード（explanatory/learning/minimal/default）あるが強度グラデーションではない |
| 4 | 3-arm 評価（terse-control アーム追加） | Partial | skill-audit は 2-arm (baseline/skill) のみ。terse-control なしで過大評価リスク |
| 5 | token delta 継続記録 | Partial | token-audit.py（14.9KB）は静的分析用。セッション間 delta 追跡なし |
| 6 | SessionStart + state file パターン | Already | session-load.js + checkpoint_recover.py で実装済み |
| 7 | 危険操作時の自動リバート | Already | careful + completion-gate.py + agency-safety-framework で実装済み |
| 8 | 入力圧縮 caveman-compress（~46% 削減） | N/A → Conditional | subscription 環境でのコンテキスト圧迫回避に潜在価値あるが、誤圧縮リスク高 |
| 9 | npx skills 多エージェント配布 | N/A | 個人 dotfiles に不要 |
| 10 | 5x API 利用（トークン課金回避） | N/A | Claude Code は subscription 課金。コスト構造が異なる |

---

## Already Strengthening Analysis (Pass 2: 強化チェック)

| # | 既存の仕組み | 記事が示す弱点/知見 | 強化案 | 判定 |
|---|---|---|---|---|
| A1 | concise.md（14行、英語前提、肯定形指示） | 日本語応答時の冗長性に対処なし（敬語・クッション語・形式文章） | 日本語 brevity セクション追加（体言止め・助詞圧縮・クッション語禁止・例外条項） | 強化可能 |
| A2 | concise.md 肯定形指示のみ | 「圧縮タスクでは禁止リスト > 肯定指示」（caveman の実証） | ## Drop List セクション追加（明示的な禁止構文） | 強化可能 |
| A3 | skill-audit 2-arm（baseline / skill） | terse-control なしで改善スコアを過大評価するリスク | Step 3 に 3-arm オプション（terse-control アーム）追加 | 強化可能 |
| A4 | MoA Synthesis Output Verbosity Guard が /review Step4 rule16 専用 | 通常応答にも適用余地あり | 全面適用は検証報告まで痩せるリスク（Codex 警告）→ 参照リンクのみ追加 | 強化可能（縮小版） |

---

## Refine: Codex + Gemini 批評

### Codex 主要批評

1. **新規性確定**: 禁止リスト型は MoA verbosity guard とは別物（語彙レベル vs 構造レベル）。重複なし
2. **5段階は過剰**: 3段階（lite/standard/ultra）で十分。認知オーバーヘッドを避ける
3. **日英混在の落とし穴**: 日本語化の真の危険は「技術説明の曖昧化」。例外条項（code/error/security/destructive confirmation は通常文）を必ず明記
4. **優先度修正**: A1+A2 > A3 > Gap#3縮小 > A4縮小
5. **A4 縮小**: Verbosity Guard の minimal 全面適用は検証報告まで痩せるリスク → 参照リンクのみ
6. **Conditional 格上げ**: 入力圧縮 caveman-compress は subscription = コンテキスト圧迫回避が本丸。ただし誤圧縮リスクで今回は見送り
7. **落とし穴列挙**: トークン削減の Goodhart 化・正確性低下・検証ログ不足・人格指示との衝突

### Gemini 信頼度評価（クォータ枯渇のため既知ナレッジベースを使用）

| 主張 | 信頼度 | 理由 |
|------|--------|------|
| 「簡潔性で 26pt 精度向上」 | 低〜中 | 出典未確認 |
| 「禁止リスト > 肯定形」 | 中 | caveman 実装で部分的に裏付け |
| 「日本語 12pt 追加削減」 | **低** | 根拠未確認。当方環境での実測検証が必要 |
| 「3-arm 評価の有効性」 | 中 | 評価設計の標準的原則と合致 |

→ 主張3の信頼度が低いため、brevity-benchmark.py による実測検証を実装タスクに組み込む

---

## Integration Decisions

### Gap / Partial

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| 1 | 日本語 brevity ルール（体言止め・助詞圧縮・クッション語禁止） | **採用** | 既存 concise.md に追加。例外条項（code/error/security/destructive confirmation は通常文）を必須で明記 |
| 2 | 禁止リスト型プロンプト（Drop: 形式） | **採用** | A1 と同ファイルに統合。肯定形と禁止形の組み合わせが効果的 |
| 3 | 3段階強度レベル（lite/standard/ultra） | **採用（縮小版）** | 5段階を3段階に縮小。output-modes.md minimal セクションを拡張 |
| 4 | terse-control アームの 3-arm 評価 | **採用** | skill-audit Step 3 にオプションとして追加。run_eval.sh 実装は保留 |
| 5 | token delta 継続記録 | **見送り** | brevity-benchmark.py で代替。静的分析と統合は将来課題 |
| 8 | 入力圧縮 caveman-compress | **見送り（Conditional）** | 誤圧縮リスクと検証コストが現状見合わず |
| 9 | npx skills 多エージェント配布 | **見送り（N/A）** | 個人 dotfiles のスコープ外 |
| 10 | 5x API 利用 | **見送り（N/A）** | subscription 環境では効果なし |

### Already 強化

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| A1 | concise.md 日本語 brevity + 例外条項追加 | **採用** | 最優先。日英混在の安全弁として例外条項が必須 |
| A2 | concise.md Drop List セクション追加 | **採用** | A1 と同ファイルに統合。明示的禁止が圧縮率向上に有効 |
| A3 | skill-audit 3-arm オプション | **採用** | terse-control なしの過大評価リスクを排除 |
| A4 | MoA Verbosity Guard 参照リンクのみ | **採用（縮小版）** | 全面適用は未検証。concise.md ultra モードに参照リンク追加のみ |

---

## Plan

### Task 1: concise.md 拡張（日本語 brevity + Drop List + 例外条項）
- **Files**: `.config/claude/output-styles/concise.md`
- **Changes**: 日本語 brevity セクション追加（体言止め・助詞圧縮・クッション語禁止）、## Drop List セクション追加、例外条項（code/error/security/destructive confirmation は通常文）明記
- **Size**: S
- **状態**: 完了

### Task 2: output-modes.md minimal 拡張（3段階強度）
- **Files**: `.config/claude/references/personas/output-modes.md`
- **Changes**: minimal モードに lite/standard/ultra の3段階強度を追加、MoA verbosity guard 参照リンク追加
- **Size**: S
- **状態**: 完了

### Task 3: skill-audit 3-arm 追加
- **Files**: `.config/claude/skills/skill-audit/SKILL.md`
- **Changes**: Step 3 に terse-control アームを加えた 3-arm 評価オプション追加。run_eval.sh 実装は保留
- **Size**: S
- **状態**: 完了

### Task 4: brevity-benchmark.py 新規作成
- **Files**: `scripts/runtime/brevity-benchmark.py`
- **Changes**: 主張3「日本語 12pt 追加削減」の実測検証用スクリプト。tiktoken による日英トークン計測、3-arm 比較出力、delta 記録
- **Size**: M（593行）
- **状態**: 完了（未実行）

### Task 5: 分析レポート保存
- **Files**: `docs/research/2026-04-11-caveman-genshijin-brevity-analysis.md`
- **Changes**: このファイル
- **Size**: S
- **状態**: 完了（このファイル）

### Task 6: 索引更新
- **Files**: `docs/research/_index.md`
- **Changes**: 「### レビュー・品質」セクション末尾に1行追記
- **Size**: S
- **状態**: このタスクで実施

---

## 次アクション（未実施）

1. **brevity-benchmark.py を実測実行**: 主張3（日本語 12pt 追加削減）を当方環境で検証
   - 依存: `uv pip install tiktoken`
   - 期待: lite/standard/ultra 各モードの実測 delta が得られる
   - 判定基準: 12pt 追加削減が確認されれば ultra モードの閾値を調整

2. **実測結果に基づいて concise.md の強度レベルを調整**: 現在の lite/standard/ultra の閾値が実態と合っているか確認

3. **3-arm 評価の run_eval.sh 実装**: 現在は SKILL.md にオプションとして記述のみ。実行側の実装は保留

---

## 落とし穴メモ（Codex 批評より）

- **Goodhart の法則**: トークン削減を目標にすると正確性・有用性が犠牲になるリスク。brevity は手段であり目的ではない
- **日英混在の曖昧化**: 技術用語・エラーメッセージは通常文でないと意味が崩れる。例外条項の維持が最重要
- **人格指示との衝突**: `/persona` スキルや人格変更系プロンプトと concise.md が競合する可能性。優先順位を明示
- **検証ログ不足**: 実測なしの80%主張は信頼度低。brevity-benchmark.py 実行まで数値を引用しない

---

## 追補: 2026-04-12 re-absorb session

同じソース記事 (mikana0918 Zenn + JuliusBrussee/caveman) を Phase 2.5 まで再分析した結果の記録。

### Phase 2 ギャップ分析 (Sonnet Explore)

| # | 要素 | 判定 | 根拠 |
|---|------|------|------|
| A | 敬語削除ルール | Already (強化可能) | 体言止め例1件のみ、です/ます 禁止が未網羅 |
| B | クッション言葉削除 | Partial | えーと/まあ/ちなみに/一応/基本的に が漏れ |
| C | ぼかし表現削除 | Already (強化可能) | 〜と思われます (受動+推量) 未列挙 |
| D | 冗長助詞圧縮 | Partial | 語形短縮ルール未定義 → 代表変換5件追加で対応 |
| E | 冗長接続圧縮 | Partial | 接続句変換ルール未定義 |
| F | 自明助詞省略 | Already (強化可能) | ultra での強度差が曖昧 |
| G | 情報水増し禁止 | Already (強化可能) | evidence 保持境界未明文化 |
| H | 破壊的操作安全弁 | Already (強化可能) | failed validation/review gate/approval も復帰条件に |
| I | 3-level gradation | Already (強化可能) | ultra 適用 gate の厳格化必要 |
| J | 実測ベンチマーク | Gap (validation) | 実装済み・未実行。初回実行で default/standard がタイムアウト |
| K | code-switching 対策 | Already (強化可能) | 判定基準未定義 |
| L | 具体例3パターン | Already (強化可能) | 実装済み・未実行 |

### Phase 2.5 批評 (Codex + Gemini 並列)

**Codex の主要指摘:**
- D を Gap → Partial に格下げ (体言止め+助詞圧縮で実質カバー)
- G/H/I を Already 強化不要 → 強化可能に昇格
- 優先度: J (benchmark) → G/H/I (gate 強化) → D (語形短縮)
- リスク: ultra 強化で verification report / Codex Review Gate の深掘りが痩せる

**Gemini の主要補完:**
- Anchored Summarization: State/Constraint は圧縮禁止、History のみ圧縮可
- Answer-First Patterning: user 向けは短く、hook/gate 内推論は完全保持
- Cascade failure: Agent A の略語指示 → Agent B が事実と誤解釈
- 記事の主戦場 (技術 QA) と dotfiles の主戦場 (harness engineering) の前提シフト

**新規要素 (Phase 2 見落とし):**
- M: 入力圧縮 (prompt compression)
- N: Anchored Summarization (State/Constraint 保護)
- O: Answer-First Patterning (2 層分離)
- P: Cascade failure 対策 (agent chain 誤伝播)

### 実施した変更 (2026-04-12)

1. **concise.md**: Drop リスト拡充 (B/C)、語形短縮ルール追加 (D)、例外条項拡張 (G/H/K/P)、2 層分離セクション新設 (N/O)、ultra gate 厳格化 (I)
2. **output-modes.md**: minimal モードの強度・例外・2 層分離を同期更新
3. **brevity-benchmark.py**: --model sonnet 追加 (nested 実行の opus[1m] 継承バグ修正)
4. **benchmark 実測 (J)**: 2 prompt × 4 arm で初回実行。default/standard がタイムアウト (120s)、lite/ultra のみ結果取得。タイムアウト延長が次の課題

### 残課題

- J: benchmark のタイムアウト調整 + 全 6 prompt での完全実行
- M: 入力圧縮の設計検討 (別セッションで)
- brevity-benchmark.py の _JA_DROP_LIST を concise.md と同期
