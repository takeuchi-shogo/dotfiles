---
source: "https://github.com/nanaism/yomiyasu (commit 1bc21f9c, v2.0.1)"
date: 2026-10-17
status: integrated
family: none
---

<!-- Phase 1.5: 既存 taxonomy のどの family にも該当せず PASS。新分野として none。近い先行分析は 2026-06-18-japanese-tech-writing-absorb-analysis.md (family: prose-writing-style) だが、この family は taxonomy に未登録 (N=1) なので飽和判定の対象外。 -->

## Source Summary

**主張**: yomiyasu は、AI が書いた日本語を「意味と条件を保ったまま」読みやすく直す Agent Skill。文体を整える前に、元の文の意味・条件・事実が書き換えで変わっていないかを検査することを重視する。

**手法**:
- SKILL.md は 110KB。標準ライブラリだけの Python が約 1MB 付属する
- lint、check/diff の検査記録(sha256 で改ざん検証)、diff の意味リスク判定、事実の復元(fact-recovery)
- 12 種の文書タイプ × 3 段階の読み手レベル、ペルソナと敬語の切り替え
- hook は opt-in。`--print-config` で設定を出力するだけで、`plugin.json` に hook の宣言はない

**根拠**: 作者のベンチマーク。ただし作者自身の lint で作者自身の出力を採点している(A/B は n=1 で、古い結果だと作者が注記)。コーパス平均の lint スコアは raw_ai 95.6 / rewritten 98.0 / human 98.7。第三者の ai-garage の検証(README が引用)では、yomiyasu を先に使う運用が 4 変種のうち可読性が最低で、時間とコストは約 4 倍。`limitations.md` の「手順の飛ばし 31/60 → 0/67」(Claude Code)は、品質でなく手順の遵守率の改善。

**前提条件**: 作者は ALGO ARTIS の社員。評価の独立性は低い。

**セキュリティ確認(grep)**: ネットワークアクセスなし。subprocess は同梱の `yomiyasu_diff.py` を起動するだけ。hook は settings を編集しない。

## Gap Analysis (Pass 1: 存在チェック)

| # | 手法 | 判定 | 詳細 |
|---|------|------|------|
| 1 | 検査記録(check/diff、sha256 検証) | Gap | 書き換え前後の対応を残す仕組みは harness にない |
| 2 | 意味差分(diff の意味リスク判定) | Gap | 書き換えで条件・数値・否定が変わったかを機械的に見る手段がない |
| 3 | 事実の復元(fact-recovery) | Gap | 同上。落ちた事実を原文から戻す手順がない |
| 4 | ペルソナ・敬語の切り替え | Gap | 文体プロファイルはあるが敬語レベルの切り替えはない |
| 5 | hook による強制 | Gap | 書き換え時に検査を強制する経路がない(yomiyasu 側も opt-in) |
| 6 | rephrase の 6 軸テスト | Partial | `japanese-ai-prose.md` は AI 臭の除去が中心で、意味保存の検査項目を持たない |
| 7 | 追加禁止ルール(no-addition) | Partial | 「適用しない場面」はあるが、書き換えで情報を足さない規則は明文化されていない |
| 8 | 12 種 × 3 段階の文書タイプ | Partial | natural-japanese は 5 種。網羅度は劣るが、足す根拠となる運用実績は未確認 |

## Already Strengthening Analysis (Pass 2: 強化チェック)

| # | 既存の仕組み | 記事が示す弱点 | 強化案 | 判定 |
|---|---|---|---|---|
| S1 | natural-japanese の `lint.py`(vendored) | 比喩的な動詞の検出がない | `lint.py` に検出を追加 | 強化可能だが撤回 |

S1 を撤回した理由は、vendored ファイルに手を入れると upstream との差分が増え、更新のたびに衝突するから。検出の追加が要るなら upstream に提案する側で扱う。

## Phase 2.5: 批評

- **Codex**: 未取得。`codex exec` が 2 回失敗した。再試行時の stderr は `ERROR: You've hit your usage limit ... try again at 9:46 PM.`。1 回目の stderr は捨ててしまったため、原因は 2 回目で確認した。
- **Gemini (agy)**: 1 回目は `--mode plan` で終了コード 0 の空出力(原因は未確認)。plan モードなしの再試行は成功した。結論は「O3(インストールせず cherry-pick)」。
  - 退けた部分: Zenn の引用が `https://zenn.dev/` というドメインだけで検証できない。「コンテキストの 20% を常時消費する」は誤り。SKILL.md 本体は呼び出し時にロードされる。ただし有効な plugin の skill 名と description は毎セッションの skill 一覧に載るので、その分の固定コストはかかる。
  - 受け入れた部分: vendored の lint は patch しない。
- Codex Review Gate (制限解除後に実行): `VERDICT: BLOCK`。指摘は「repo の settings.json は live に反映されないので provisioning も override も効かない」で、`nix/home/default.nix` の「settings.json は意図的に非管理」と照合して正しいと確認した。反映手順を下の Task 1/2 に明記して対応した。

## Integration Decisions

### Gap / Partial

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| 1-3 | 検査記録・意味差分・事実復元 | スキップ(自前では取り込まない) | yomiyasu を plugin として入れれば、必要なときにその機能を使える。harness に複製すると 1MB 規模の保守を抱える |
| 4 | ペルソナ・敬語 | スキップ | yomiyasu 側で足りる。自前の需要は未確認 |
| 5 | hook 強制 | スキップ | 作者の検証で時間とコストが約 4 倍。強制すると全書き換えに乗る |
| 6-7 | 6 軸テストと追加禁止 | 採用 | `japanese-ai-prose.md` に「書き換えで意味を変えない」節として入れる。plugin を使わない場面にも効く |
| 8 | 文書タイプ 12 種 | スキップ | 5 種で困った実績がない |

### Already 強化

| # | 項目 | 判定 | 理由 |
|---|------|------|------|
| S1 | `lint.py` への比喩動詞検出 | スキップ | 上記のとおり、vendored への patch は upstream drift を増やす |

### ユーザー判断(Phase 3)

ユーザーは yomiyasu を自動で発火させたい。natural-japanese を常時オンにするつもりはなく、導入形態は plugin を希望した。これを受けた決定は次のとおり。

- yomiyasu を plugin として入れる。repo の `settings.json` には新 PC の雛形として書き、この PC の live 設定には CLI で入れる (Task 1)。
- natural-japanese は `skillOverrides` で `user-invocable-only` にする。トリガーの衝突を止めるため、PR #247 の stop-ai-slop-jp と同じ扱い。
- 役割分担: yomiyasu は書き上がった下書きの書き直し(自動)。natural-japanese は新規執筆・採点・文体プロファイル(`/natural-japanese` で明示起動)。
- 採用しないもの: vendoring、hook、検査記録のワークフローを harness に組み込むこと。

## Plan

### Task 1: yomiyasu を plugin として導入
- **Files**: `.config/claude/settings.json`(`extraKnownMarketplaces` / `enabledPlugins`)
- **Changes**: marketplace と plugin を追加。live の `~/.claude/settings.json` は意図的に非管理 (`nix/home/default.nix`) で、repo の値は新 PC で手動 cp するときの雛形にしかならない。この PC には `claude plugin marketplace add nanaism/yomiyasu` と `claude plugin install yomiyasu@yomiyasu --scope user` で入れる
- **Size**: S

### Task 2: natural-japanese を user-invocable-only に
- **Files**: `.config/claude/settings.json`(`skillOverrides`)
- **Changes**: natural-japanese に `user-invocable-only` を設定。live にも同じキーを jq で足す (repo から live へ同期されるのは `permissions` だけ)
- **Size**: S

### Task 3: 意味を変えない書き換え節の追加
- **Files**: `.config/claude/references/japanese-ai-prose.md`
- **Changes**: 「書き換えで意味を変えない」節を追加(追加禁止 + 6 軸の rephrase 確認)
- **Size**: S

## 撤退条件

- yomiyasu の自動発火が文章以外のタスクで起きる、またはトークンコストを実感したら、plugin を disable する。
- natural-japanese を使えなくて困ったら、`skillOverrides` を元に戻す。
- marketplace は pin していない(HEAD 追従)。他の 7 marketplace と同じ扱いで、更新で upstream の変更が入る。更新時に CHANGELOG を確認する。

## 未解決

- なし。並行 worktree `worktrees/nj-tpl`(branch `docs/natural-japanese-templates`)を確認した (2026-10-18)。差分は完了済み計画 `docs/plans/completed/2026-09-28-natural-japanese-claude-config-plan.md` を閉じる 1 ファイルだけで、natural-japanese の自動発火は前提にしていない。
