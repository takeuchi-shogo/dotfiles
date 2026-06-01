---
title: "Suzanne teach-back prompt (Anthropic, via Thariq) — absorb analysis"
date: 2026-06-02
source:
  title: "teacher-mode prompt for staying in the loop with Claude's work"
  author: Suzanne (Anthropic) / shared by Thariq Shihipar (@trq212)
  url: https://gist.github.com/ThariqS/1389dcdff9eba4789887a2211370f06b
  type: gist
status: implemented
family: agent-comprehension
adopted: 1
---

## Source Summary

**主張**: Claude が行った作業を人間が「ループに入って完全に理解する」ため、Claude を賢い教師役にして、人間の理解度を段階的に検証してからセッションを終える teacher-mode プロンプト。

**手法**: (1) 段階的習得ゲート (2) running md チェックリスト (3) 3階層理解 problem/solution/broader-context + why 深掘り (4) restate-first (5) ELI5/ELI14/ELI-intern 適応説明 (6) AskUserQuestion クイズ (正答シャッフル・提出まで非開示) (7) コード提示/debugger (8) `/goal` 完了ゲート (理解検証まで終わらない)

**根拠**: Anthropic 社内実践 (Suzanne)、Thariq お気に入り。逸話的・社会的証明のみ、データなし。学習科学的には self-explanation effect / protégé effect / retrieval practice として裏付けあり。

**前提条件**: Claude が実質作業をした後、人間がそれを深く理解したい時。対話的セッション、AskUserQuestion・debugger が必要。

## Gap 分析 (Phase 2)

| # | 手法 | 判定 | 現状 |
|---|------|------|------|
| 1 | 段階的習得ゲート | Partial | `deep-read` は phase 進行するが習得確認ゲートなし |
| 2 | running md チェックリスト | Gap | なし |
| 3 | 3階層理解 (セッション作業向け) | Gap | `deep-read` は外部記事の thesis/evidence 用 |
| 4 | why 深掘り | Already | `deep-read` Phase 2 |
| 5 | restate-first | Partial | `deep-read` は部分的 |
| 6 | ELI5/14/intern | Gap (小) | なし |
| 7 | クイズ (シャッフル/非開示) | Already | `quiz` command |
| 8 | コード/debugger 活用 | Gap | 学習文脈になし |
| 9 | `/goal` 完了ゲート | Partial | `deep-read` は user 停止まで、hard gate なし |

**核心**: 既存 `deep-read`=外部記事理解、`quiz`=CC セットアップ知識、`think`=意思決定、`recall`=履歴復元。いずれも **「Claude がこのセッションで行った作業を本人に教え返し理解検証する」** 責務を持たない = クリーンな Gap。

## Phase 2.5 Refine (Codex)

Codex (gpt-5.5, read-only) 批評で判断を補正:
- (a) **deep-read 拡張は反対** — 外部記事理解と trigger が濁る。別物が正しい
- (b) Already (quiz/think/recall) は Partial 止まり — 責務が異なる
- (c) **★いきなり重い skill を作るな** — まず reusable prompt で十分。2-3 回使って残れば skill 化 (Pruning-First)
- (d) 最優先 = "session closing mastery checklist": restate-first → problem/solution/edge-cases 3段階 → why-drill 1回 → 小テスト1問。`/goal` hard gate は強力だが毎回は摩擦高 → **opt-in 推奨**

(Gemini grounding は単一プロンプトソースで自明なため省略。bias-mitigation は非 Claude モデル Codex で達成)

## 採用 (1 件)

**`/teachback` コマンド新設** (`.config/claude/commands/teachback.md`, S 規模):
- Codex 推奨の中庸 = 重い skill ではなく軽量 command (= 再利用プロンプト)
- 引数 `--strict` で `/goal` hard gate を opt-in (デフォルトは終了を妨げない)
- 3階層チェックリスト + restate-first + why 深掘り + AskUserQuestion クイズ (シャッフル/非開示) + ELI5/14/intern + debugger を統合
- 対象を「このセッションの変更」に限定し、外部記事 (`/deep-read`)・CC 知識 (`/quiz`) とルーティング分離

**不採用**: フル skill 化 (使用頻度未確認、Pruning-First)。2-3 回使って定着したら skill 昇格を検討。

## Validation-only Follow-up (副次)

absorb 中の Phase 2.5 で **cmux Worker (`scripts/runtime/launch-worker.sh`) のバグを発見・修正** (user 要望でスコープ追加):
- **真因**: cmux の surface ref はグローバル (現 surface:50+)。script が `--surface surface:1` をハードコードしていたが、新ワークスペースの実 surface は別 ref → `workspace:N` 内に surface:1 が存在せず `Surface not found` で codex/gemini worker 起動が全失敗
- **修正**: `new-workspace` 後に `list-pane-surfaces --workspace "$WS"` で実 surface ref を動的解決 (リトライ付き)、`surface:1` を全置換。`new-workspace` の name も positional → `--name` に修正
- **検証**: codex worker ライブ起動で `OK surface:56 workspace:22` を確認、エラー解消
- これにより `/absorb` Phase 2.5 の正規パス (cmux Worker 優先) が復旧
