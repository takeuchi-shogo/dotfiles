---
source: "【保存版】Codex vs Claude Code：数百時間使ってたどり着いた"最強の役割分担" (Codex Studio @Codestudiopjbk, 2026-04 末)"
date: 2026-04-29
status: analyzed
vendor_bias: HIGH — Codex Studio は Codex 推し 3 人運営、上場企業との Codex AI 共同開発、DM 相談募集
---

## Source Summary

**著者バイアス警告**: Codex Studio は Codex ガチ勢 3 人運営アカウント。主張全体に割引が必要。

**主張**:
1. Codex / Claude Code は「ツール」、GPT-5.5 / Opus 4.7 は「頭脳」。区別して運用せよ
2. タスク種類で使い分けるのが最適（どちらが勝ちではない）

**手法 12 個**:
- A. Tool/Brain (harness vs model) 分離フレーム
- B. 用途別ルーティング 6 軸（壊れたコード→Codex / 日本語仕上げ→Claude Code / 安全側→Codex / 長時間→Claude Code / 実務文→GPT-5.5 / 色気のある日本語→Opus 4.7）
- C. Codex 安全設計 deny by default 哲学
- D. Claude Code MCP / Hook / custom command 拡張性
- E. Opus 4.7 tokenizer +35% トークン消費警告
- F. GPT-5.5 token burn rate（週次上限 2 日で尽きる anecdote）
- G. Codex 4/23 in-app browser / 自動レビュー機能
- H. 長時間自律実行ワークフロー
- I. 日本語コピー品質差（Opus > GPT-5.5）
- J. tool error 1/3 削減言及
- K. Codex の「設計から直す」rewrite 提案傾向
- L. Anthropic 4/23 quality disclosure

---

## Gap Analysis (Pass 1: 存在チェック)

| # | 手法 | 判定 | 詳細 |
|---|------|------|------|
| A | Tool/Brain 分離 | Already | CLAUDE.md + harness-engineering-absorb-analysis.md に内包済 |
| B | 用途別ルーティング | Already | `references/model-routing.md` で 6 モデル × 用途マトリクス完備 |
| C | Codex deny by default | Partial | `.codex/config.toml` の sandbox 設定は存在するが dotfiles は trusted profile 前提 |
| D | MCP/Hook/custom command 拡張性 | Partial | `docs/agent-harness-contract.md` + `tool-scoping` でカバー済 |
| E | Opus 4.7 tokenizer +35% | Gap | `references/model-routing.md` にコスト注記なし |
| F | GPT-5.5 token burn rate | N/A | anecdote 単独、週次上限はプラン次第 |
| G | Codex 4/23 in-app browser/自動レビュー | Gap | `references/model-routing.md` に機能更新なし |
| H | 長時間自律実行 | Already | `/autonomous` + blueprint pattern で実装済 |
| I | 日本語コピー品質差 | N/A | ケース 1 つで一般化不可 |
| J | tool error 1/3 削減 | N/A | metric 出典不明 |
| K | Codex rewrite 提案傾向 | Partial | `codex-delegation.md` に apply_patch 行番号注意あり |
| L | Anthropic 4/23 quality disclosure | Gap | 公式ブログで未確認 |

---

## Phase 2.5: マルチモデル批評

### Codex (codex:codex-rescue) の判定

**採用 0 件が妥当**という判定。

1. **見落としなし**: model-routing / codex-delegation / autonomous / blueprint / codex-plan-reviewer で役割分担と長時間実行は既に厚い
2. **過大評価**: E / G / L は repo 内で一次確認できず。C も `.codex/config.toml` は trusted 前提なので「deny by default」と一般化して取り込むのは危険
3. **過小評価なし**: A/B/H の Already 強化不要は妥当。K の rewrite 傾向も codex-delegation.md に行番号・apply_patch 前提注意あり
4. **前提の誤り**: 著者の前提は「Claude orchestrator なし、Codex/Claude Code を直接切り替える」。dotfiles の「Claude orchestrator + Codex deep review」設計とは根本的に違う
5. **優先度**: Pruning-First では採用ゼロ。残すなら「trusted profile では Codex safety claim を過信しない」を `codex-delegation.md` に 1 行のみ

### Gemini (gemini-explore) の事実確認

6 主張のうち**公式裏取り可能なのは 2 つだけ**（Opus 4.7 release 自体 / GPT-5.5 API 公開日 4/24）。

| 主張 | 裏取り結果 |
|------|-----------|
| E: Opus 4.7 tokenizer +35% | Anthropic docs に記載なし、実験値の可能性 |
| G: Codex 4/23 in-app browser/自動レビュー | 公式 changelog でエントリ確認不可 |
| L: Anthropic 4/23 quality disclosure | 公式 blog で見当たらない |
| F: GPT-5.5 ChatGPT ログイン必須 | API キー vs セッション制御は OpenAI 公式 docs で詳細未公開 |

Gemini 推奨: 公式情報に基づく cost/performance 実測 + task タイプ別ルーティング（既に実装済）

---

## Triage 結果

**採用: 1 件（Codex safety 過信しない注記のみ）**

| # | 手法 | 最終判定 | 理由 |
|---|------|---------|------|
| A | Tool/Brain 分離 | Reject (Already) | — |
| B | 用途別ルーティング | Reject (Already) | — |
| C | deny by default | **Reject** | trusted profile 前提と矛盾。代わりに「過信しない」注記 1 行のみ採択 |
| D | 拡張性説明 | Reject (Already) | agent-harness-contract で十分 |
| E | tokenizer +35% | Reject | 公式裏取り不可 |
| F | GPT-5.5 burn rate | Reject (N/A) | anecdote 単独 |
| G | Codex 4/23 新機能 | Reject | 公式 changelog 確認不可 |
| H | 長時間自律実行 | Reject (Already) | — |
| I | 日本語品質差 | Reject (N/A) | n=1 |
| J | error 1/3 削減 | Reject (N/A) | 出典不明 |
| K | Codex rewrite 傾向 | Reject (Already) | codex-delegation.md に内包済 |
| L | quality disclosure | Reject | 公式裏取り不可 |

**唯一の採択**: `rules/codex-delegation.md` に「Safety Claim を過信しない」セクション追記（S 規模、1 ファイル、約 4 行）

---

## 実装結果

`/Users/takeuchishougo/dotfiles/.config/claude/rules/codex-delegation.md` L120 直後に追記済（ユーザー提示の Phase 4 完了情報より）:

```markdown
## Safety Claim を過信しない

Codex は sandbox / deny-by-default を設計原則とするが、dotfiles 運用は **trusted profile 前提**で動く。
実際の safety boundary は (1) `.codex/config.toml` の profile 設定、(2) lefthook pre-commit、
(3) `protect-linter-config` hook の 3 層で構成される。
「Codex が安全」という主張をそのまま信頼せず、自分の harness の設定を一次情報にせよ。
```

---

## Lessons Learned

1. **著者バイアスを Phase 0 で明示的に検出する**: Codex Studio = Codex 推し DM 募集アカウント → 主張全体に割引が必要。バイアス警告は分析前提に記載すべき
2. **公式 changelog/docs で裏取りできない主張は採用しない**: E/G/L はいずれも一次情報確認不可。anecdote や「〜と言われている」は採用根拠にならない
3. **「業界全体でこう言われている」≠「自分の harness ではこう運用している」**: deny by default は理想だが trusted profile 運用の現実を反映する必要がある。一般論を harness ルールに直翻訳すると矛盾が生じる
4. **Codex 批評の前提チェックが重要**: 著者前提（Codex/Claude Code を直接切り替え）と dotfiles 設計（Claude orchestrator + Codex deep review）が根本的に違うことを早期に検出できれば、分析コストを削減できた

---

## 後処理 Status

- [ ] MEMORY.md に索引エントリ追記（`research/2026-04-29-codex-vs-claudecode-role-split-absorb-analysis.md`）
- [ ] Obsidian wiki に absorb ログ追記
- [ ] `docs/research/_index.md` に本ファイルを追記（統合済み扱い）
- [ ] `rules/codex-delegation.md` の Safety Claim セクション追記を git commit
