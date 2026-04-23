# ADR-0006: Hook 採用判断の 3 分類

## Status

Accepted

## Context

グローバル `.claude/CLAUDE.md` は「static-checkable rules は mechanism に寄せる」
「review/gate は pass/block 判定」と定めており、hook / linter / gate による
deterministic enforcement を志向している。

一方、Andrej Karpathy の LLM coding guidelines (`CLAUDE.md` の 4 原則) は
「Hard enforcement NG。instruction に埋め込む soft nudge で動かせ」と明言している。
4 原則 (Think Before Coding / Simplicity First / Surgical Changes / Goal-Driven Execution)
は「判断の質」を上げる instruction であり、regex や pre-commit で機械判定することに
意味がない。仮定明示を regex で block しても形式的な「Assumptions」欄が増えるだけで、
思考は増えない。

この緊張を解消しないまま hook を増やし続けると、以下のリスクが生じる:

- semantic judgment を deterministic 化した hook が false positive を量産し、
  push back の自由度を削る
- Karpathy 原則を regex で「chkeck したフリ」にしてしまう儀式化
- harness debt が累積し、hook 自身の staleness を監視するメタ hook が必要になる

## Decision

hook / gate / lint 追加判断を **3 分類** で運用する。どの分類に属するかを
commit メッセージまたは PR 説明で明示し、分類に応じた実装レベルを選ぶ。

### 1. Deterministic Block

機械的に判定可能で、外部から検証可能な safety boundary。block してよい。

- **条件**: (a) 入力だけで pass/fail が一意に決まる、(b) 違反が明確な損失 (security / data / reproducibility) を引き起こす、(c) 人間判断が挟まらない
- **実装**: `exit 2` で block、hook で自動適用
- **既存例**:
  - `protect-linter-config.py` — リンター設定ファイルの変更を block
  - `spec-quality-check.py` 内の明確な欠落検知
  - test failure / secret detection / `git commit --no-verify` 禁止

### 2. Semantic Advisory

判定に semantic judgment が必要だが、pattern として警告する価値があるもの。warn のみ、block しない。

- **条件**: (a) pattern マッチで「疑わしい」ケースを検出できる、(b) ただし false positive が避けられない、(c) 最終判断は人間・LLM が行う
- **実装**: `exit 0` で stdout に WARN 出力、blocking しない
- **既存例**:
  - `change-surface-advisor.py` — 変更規模や近接ファイルの advisory
  - `impact-scan` PostToolUse hook — 参照先ファイルの一覧通知
  - `file-proliferation-guard` — 新規ファイル作成の warn

### 3. Human Judgment (Instruction Only)

判断の質そのものを問う項目。hook / lint 対象外。instruction / skill / review で扱う。

- **条件**: (a) 何が「正しい」かが文脈依存、(b) regex / static rule では捕捉できない、(c) 強制すると儀式化して逆に質が下がる
- **実装**: `CLAUDE.md` / skill / rules / ADR に記述のみ。hook は作らない
- **既存例**:
  - Karpathy 4 原則 (Think Before Coding / Simplicity First / Surgical Changes / Goal-Driven Execution)
  - 「adjacent code を改善しない」
  - 「仮定を明示する」
  - code review の pass/block 判定 (人間 or LLM の判断が必須)

## Consequences

### Positive
- hook 追加判断に基準ができ、「Karpathy 原則を regex で enforce」のような哲学違反を防げる
- 既存 hook の分類が事後的に整理され、staleness 監査時に「どれを残すか」の判断が速くなる
- Karpathy 4 原則を hook で捕捉しようとする誘惑を排除 (instruction のまま残す根拠が明確)

### Negative
- 3 分類の境界が曖昧な case で議論が発生する (特に Advisory と Human Judgment の境界)
- Deterministic Block と Semantic Advisory の混同を防ぐため、hook 側の exit code / stdout 形式を統一する運用が必要

### Neutral
- 既存 hook の挙動は変更しない。本 ADR は判断枠組みを事後整理するのみ
- Cursor / Codex 側でも「root `CLAUDE.md` の Karpathy 原則は Human Judgment 分類」として同じ扱いをする

## Appendix: ThoughtWorks 4 軸分類との関係 (2026-04-24 追加)

Birgitta Böckeler (ThoughtWorks) は harness controls を 2 軸で分類する:

- **Guide (before) vs Sensor (after)**: agent が動く前の制約か、動いた後の観測か
- **Computational (deterministic) vs Inferential (LLM-based)**: 機械判定か意味判定か

本 ADR の 3 分類は「hook を追加すべきか」の採用基準であり、4 軸分類は「どんな種類の制御か」の設計語彙で、**直交する**。両方を併用できる。

### マッピング例

| 本 ADR の 3 分類 | 4 軸象限 | 例 |
|-----------------|----------|-----|
| Deterministic Block | Computational × Guide/Sensor | `protect-linter-config.py` (Guide / PreToolUse)、`golden-check.py` (Sensor / PostToolUse) |
| Semantic Advisory | Inferential × Guide/Sensor | `codex-reviewer` (Sensor / post-change)、`suggest-gemini.py` (Guide / pre-delegation) |
| Human Judgment | (4 軸外) | Karpathy 4 原則、instruction 埋め込み |

### 使いどころ

- **抜け漏れ監査**: 4 軸分類で全体を俯瞰し、「Computational Guide が 0 個になっていないか」「Inferential Sensor に頼りすぎていないか」を確認
- **個別 hook 採用判断**: 本 ADR の 3 分類を使う (Deterministic Block / Semantic Advisory / Human Judgment のどれか)

**由来**: AlphaSignal "A Closer Look at Harness Engineering from Top AI Companies" (2026-04)、`docs/research/2026-04-24-harness-engineering-absorb-analysis.md`

## References

- `CLAUDE.md` (project) — Karpathy 4 原則本体
- `.config/claude/references/agency-safety-framework.md` — 権限境界の既存フレームワーク
- `.config/claude/references/tool-scoping-guide.md` — Interactive vs unattended の block 判断
- `.config/claude/references/harness-debt-register.md` — hook staleness 監査
- ADR-0001 (Hook 4 層分離) — hook 層別の役割
- ADR-0004 (リンター設定保護) — Deterministic Block の代表例
- `docs/research/2026-04-24-harness-engineering-absorb-analysis.md` — ThoughtWorks 4 軸分類の出典
