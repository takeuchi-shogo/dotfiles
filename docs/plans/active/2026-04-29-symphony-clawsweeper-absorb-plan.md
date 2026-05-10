---
status: active
last_reviewed: 2026-04-29
related_research: docs/research/2026-04-29-symphony-clawsweeper-absorb-analysis.md
---

# Symphony / ClawSweeper Absorb — Janitor Hardening Plan

## Goal

OpenAI Symphony (2026-04-27) と ClawSweeper (2026-04-25) の記事公開時点で、dotfiles は既に Symphony Pilot と Codex Janitor を取り込み済み。本プランは「記事の primitives を新規取り込みする」のではなく、**既存の Codex Janitor をハーデニングする** 形で 3 グループの強化を行う。

Pruning-First で原則「新規追加より既存強化」。

## Source

- 記事: `https://alphasignal.ai/.../symphony-clawsweeper` (AlphaSignal, 2026-04-28)
- 分析: `docs/research/2026-04-29-symphony-clawsweeper-absorb-analysis.md`
- 既存 Symphony Pilot: `docs/workflows/symphony/WORKFLOW.md`, `docs/playbooks/symphony-pilot.md`
- 既存 Codex Janitor: `tools/codex-janitor/`, `docs/playbooks/codex-janitor-workflow.md`

## Decision Lens

| 観点 | 判定 |
|------|------|
| Symphony 本体採用 | 既に pilot として導入済 (`docs/playbooks/symphony-pilot.md`)。本プランは無関係 |
| ClawSweeper 本体採用 | **棄却**: Always-on daemon は symphony-pilot.md L24-28 で "Not adopted yet" と明言。tier cron / shard parallel / apply cap は個人 dotfiles で over-engineering |
| 採用方針 | Janitor の **既存 TODO 消化 (F0)** + ClawSweeper safety primitives の中で個人 dotfiles で実害をなくすもの (#9+#10, #13+#11) のみ |

## Scope

### グループ F0: Janitor Follow-Ups（最優先・既存 TODO 消化）

**根拠**: `docs/playbooks/codex-janitor-workflow.md` L66-72 に "no-op diff / validation failure summary / token budget" の Follow-Ups が TODO 化されている。Codex 批評で「新規取り込みより先に既存 TODO を片付けるべき」と指摘。

**変更ファイル:**
- `tools/codex-janitor/runner.py` — stop rule infrastructure 拡張（3 stop conditions 追加）
- `tools/codex-janitor/workflows/refactor-loop.toml` — stop_rules セクション追加
- `tools/codex-janitor/tests/test_*.py` — stop rule 単体テスト
- `docs/playbooks/codex-janitor-workflow.md` — Follow-Ups セクション更新

**Stop conditions 詳細:**
1. `no-op diff`: stage 完了後の `git diff --quiet` が clean → skip 判定
2. `validation failure summary`: validation コマンド (task validate-configs 等) が non-zero → 失敗を manifest に記録して停止
3. `token budget`: 累積 token usage（or wall clock 時間）が threshold 超過 → 停止

### グループ #9+#10: Snapshot Hash 付き構造化 Evidence Record

**根拠**: Codex 批評で `runner.py:448-457` の manifest.json + stdout.jsonl + last-message.txt は raw/manifest 保存のみで構造化 evidence record（ClawSweeper 形式の decision + evidence + snapshot hash）が未実装と判定。

**変更ファイル:**
- `tools/codex-janitor/runner.py` — manifest.json schema 拡張 + snapshot 計算 + drift detection
- `tools/codex-janitor/tests/test_*.py` — snapshot/drift 単体テスト
- `docs/playbooks/codex-janitor-workflow.md` — "Single-run Drift Detection" セクション追加

**manifest.json schema 拡張:**
```json
{
  "snapshot_start": { "commit": "<sha>", "files_sha256": {} },
  "snapshot_pre_apply": { "commit": "<sha>", "files_sha256": {} },
  "stages": [
    {
      "name": "implement",
      "decision": { "verdict": "proceed|skip|stop", "reason": "..." },
      "evidence": [{ "kind": "stdout|test|usefulness_score", "ref": "..." }]
    }
  ]
}
```

**Stop condition 追加:**
4. `snapshot_drift`: `snapshot_start.commit != snapshot_pre_apply.commit` または影響ファイル sha256 が一致しない → apply 段階を skip

**重要 (Gemini 警告踏まえた scope 限定)**: 個人 dotfiles では手動編集による drift が頻発する。本機能の scope は **単一 run 内の review→apply 整合性のみ**。**cron tier 化や cross-run snapshot 比較は本プランの対象外**。playbook で明示する。

### グループ #13+#11: Keep-Open Bias + Token Strip（軽量追記）

**根拠**: 
- #13: improve-policy.md L637-643 で半分カバー済。Janitor 側にも明示する
- #11: profiles.review が read-only sandbox なので実害は顕在化していないが、`GITHUB_TOKEN` / `LINEAR_API_KEY` を物理削除する物理ガードはあって損しない（playbook 記述レベル）

**変更ファイル:**
- `tools/codex-janitor/workflows/refactor-loop.toml` — stop_rules に "destructive_without_evidence" 追加
- `docs/playbooks/codex-janitor-workflow.md` — "When in doubt, skip" 原則を 1 行追加（improve-policy.md と相互参照）
- `.codex/config.toml` — profiles.review に env strip コメント注記（実装は wrapper script、別タスクで対応可）
- `docs/playbooks/symphony-pilot.md` — Safety Posture に "Token-stripped review" を 1 行追加

**Stop condition 追加:**
5. `destructive_without_evidence`: stage diff が destructive operation を含み、かつ evidence_chain の confidence ≤ 0.5 → skip

## Out of Scope（明示棄却）

| 項目 | 棄却理由 |
|------|---------|
| Tiered cron scheduling (hot/warm/cold) | Always-on daemon を Not adopted (symphony-pilot.md L24-28)。個人 dotfiles で tier 化は over-engineering |
| Apply cap (50 fresh per checkpoint) | improve-policy.md L605-650 の `resource_targets ≤ 2` + 3要素同時変更禁止 で個人規模 blast radius は十分 |
| Codex App Server 全面採用 | Codex Janitor が意図的に `codex exec` ベース。Symphony pilot WORKFLOW のみ app-server 指定。二系統共存方針を維持 |
| Sharded parallel review (313×100) | max_concurrent_agents=1 が個人 dotfiles の現行最適 (symphony-pilot.md L62-63) |
| GitHub issue cron pipeline | `/improve` の `gh issue list --label autoevolve` で代替済 |
| Cross-run snapshot compare | drift 頻発で開発体験を損なう（Gemini 警告） |

## Constraints

- `codex exec` / `codex exec resume` 現行 stable CLI を優先（実機 v0.124.0 確認済）
- destructive command や sandbox bypass を前提にしない
- 既存の `codex-search-first`, `dotfiles-config-validation`, `codex-checkpoint-resume`, `codex-verification-before-completion` skill と競合しない
- 実装中も `task codex-janitor -- --dry-run --improvements 1 --reviews 1` が通ること
- snapshot drift detection は **single-run scope only**

## Validation

各グループ完了後の必須チェック:

```sh
python3 -m unittest discover -s tools/codex-janitor/tests -p 'test_*.py' -v
task validate-configs
task validate-readmes
task codex-janitor -- --dry-run --improvements 1 --reviews 1
```

`.codex/config.toml` を変えた場合:

```sh
task validate-symlinks
```

## Steps（実装順序）

### Phase 1: F0（Janitor Follow-Ups）

1. `runner.py` の stop rule infrastructure をリファクタ（既存 `skip` / `usefulness_score` / `non_zero_exit` / `session_lost` を共通 `StopRule` 抽象に揃える）
2. `no-op diff stop`: stage 完了後 `git diff --quiet` を判定する関数追加
3. `validation failure summary stop`: validation command を runner から起動し non-zero で停止 + summary 記録
4. `token budget stop`: 累積 token usage（CLI 出力から parse、または wall clock）の threshold 設定
5. `refactor-loop.toml` に `[stop_rules]` セクション追加（threshold 値を config 化）
6. tests 追加: 各 stop rule の trigger / non-trigger 単体テスト
7. `docs/playbooks/codex-janitor-workflow.md` Follow-Ups L66-72 を「Implemented in Phase 1 (2026-04-29)」へ更新

### Phase 2: #9+#10（Snapshot Hash 構造化 Evidence Record）

1. `runner.py` に `compute_snapshot()` 関数追加（git commit + 影響ファイル sha256）
2. manifest.json schema 拡張（`snapshot_start`, `snapshot_pre_apply`, stage ごとの `decision` / `evidence`）
3. apply 直前で `snapshot_pre_apply` を計算 → `snapshot_drift` stop rule trigger
4. tests 追加: snapshot 計算 / drift 検知 / drift なし時の正常進行
5. playbook に "Single-run Drift Detection" セクション追加（cron tier 化しない注意点を明記）
6. existing tests が壊れないこと確認

### Phase 3: #13+#11（Keep-Open Bias + Token Strip）

1. `refactor-loop.toml` の `[stop_rules]` に `destructive_without_evidence` を追加
2. `runner.py` に destructive operation 検出（git diff の `--stat` で削除行数 / 大規模置換閾値）
3. `codex-janitor-workflow.md` に "When in doubt, skip" 原則 1 行（improve-policy.md と相互参照）
4. `.codex/config.toml` の `[profiles.review]` に `# Token strip: GITHUB_TOKEN/LINEAR_API_KEY` コメント注記
5. `symphony-pilot.md` Safety Posture に "Token-stripped review" 1 行追加

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Stop rule の false-positive で Janitor が早期終了 | M | configurable threshold + `--dry-run` で挙動確認、`--allow-noop` 等のオーバーライドフラグ追加 |
| snapshot drift detection で個人手動編集と衝突 | H | scope を single-run 内に限定、cron tier 化禁止を playbook に明記 |
| Token strip で Codex 認証失敗 | L | `profiles.review` は read-only。`OPENAI_API_KEY` は維持、`GITHUB_TOKEN/LINEAR_API_KEY` のみ unset。実装は wrapper script で分離 |
| Schema 変更で既存 manifest 破壊 | M | backward-compatible に拡張（既存 keys 保持）。既存 manifest の migration script は不要（tmp/codex-janitor/ 配下は ephemeral） |

## Rollback / Reversibility

- 全変更は git revert 可能（新規ファイル追加なし、既存ファイルへの追記のみ）
- 撤退条件: 
  - stop rule で Janitor が完走しなくなる → 該当 stop rule を `enabled = false` に切り替え
  - snapshot drift が個人 dotfiles で頻発し friction → drift detection を `enabled = false` で無効化
  - Token strip で Codex 認証失敗 → wrapper script を bypass

参照: `references/reversible-decisions.md`

## Pre-mortem（失敗モード）

| 失敗 | 兆候 | 対策 |
|-----|------|------|
| Stop rule が複雑化して Janitor の挙動が読めなくなる | manifest.json で stop reason が空 / 不可解 | 各 stop rule に明示的 `reason` 文字列を必須化 |
| Snapshot 計算が遅すぎて Janitor が体感遅い | 1 run あたり >5 秒の遅延 | 影響ファイルだけ sha256 化（all-files は計算しない） |
| 構造化 evidence record が冗長化して human review 不能 | manifest.json が 100KB 超 | top-level summary フィールド追加、詳細は stages 配下 |

参照: `references/pre-mortem-checklist.md`

## Acceptance Criteria

- [ ] Janitor の stop rule に **5 件すべて wired**: no-op-diff / validation-failure / token-budget / snapshot-drift / destructive-without-evidence
- [ ] `manifest.json` に `snapshot_start`, `snapshot_pre_apply`, stage ごとの `decision` / `evidence` セクション
- [ ] `tools/codex-janitor/tests/` に新規 stop rule 単体テスト + snapshot/drift テストすべて pass
- [ ] `task codex-janitor -- --dry-run --improvements 1 --reviews 1` が成功する
- [ ] `task validate-configs` / `task validate-readmes` 通過
- [ ] `docs/playbooks/codex-janitor-workflow.md` Follow-Ups L66-72 が "Implemented" 化、新セクション "Single-run Drift Detection" + "When in doubt, skip" 追加
- [ ] `docs/playbooks/symphony-pilot.md` Safety Posture に "Token-stripped review" 追加
- [ ] `.codex/config.toml` profiles.review に env strip コメント注記

## Estimated Size

| Group | Files | LOC | Size |
|-------|-------|-----|------|
| F0 | 4 | ~150 | M |
| #9+#10 | 3 | ~120 | M |
| #13+#11 | 4 | ~30 | S |
| **Total** | **~9 files** | **~300 LOC** | **L** |

→ **L 規模**。新セッションで `/rpi docs/plans/active/2026-04-29-symphony-clawsweeper-absorb-plan.md` で実行を推奨。

## Progress

- [x] Phase 1: F0 (Janitor Follow-Ups) — 2026-04-29 実装完了
- [x] Phase 2: #9+#10 (Snapshot Hash + 構造化 Evidence Record) — 2026-04-29 実装完了
- [x] Phase 3: #13+#11 (Keep-Open Bias + Token Strip) — 2026-04-29 実装完了

**実装サマリ (2026-04-29)**:
- `runner.py`: 5 stop rules 統合 (no_op_diff / validation / time_budget / snapshot_drift / destructive_without_evidence)
- `refactor-loop.toml`: `[stop_rules.*]` 5 セクション追加
- `manifest.json` schema: `snapshot_start` / `snapshot_pre_apply` / stage ごとの `decision` + `evidence` 拡張
- `test_runner.py`: 既存 3 + 新規 18 = 21 テスト全 pass
- `codex-janitor-workflow.md`: Follow-Ups Implemented + "Single-run Drift Detection" + "When in doubt, skip" 追加
- `symphony-pilot.md`: Safety Posture に "Token-stripped review" 追加
- `.codex/config.toml`: `[profiles.review]` に env strip コメント注記

**Validation 結果**:
- ✅ `python3 -m unittest discover -s tools/codex-janitor/tests` (21/21 pass)
- ✅ `task validate-configs`
- ✅ `task codex-janitor -- --dry-run --improvements 1 --reviews 1`
- ✅ `task validate-symlinks`
- ⚠ `task validate-readmes` は cloudflare-deploy skill の既存 broken symlink で fail（本変更と無関係、commit `4e957a2` 由来）

**残課題 (別タスクで対応)**:
- token strip wrapper script の実装（playbook 記述レベルに留める方針を維持）
- `runner.py` 行数 866 行 (閾値 300 超過) → 将来モジュール分離 (`runner.py` / `stop_rules.py` / `snapshot.py`) を `references/harness-debt-register.md` に記録すべき

## Decision Log

- ClawSweeper 本体（cron tier / shard parallel / apply cap）は棄却。symphony-pilot.md L24-28 の "Not adopted yet" 方針を維持
- Codex 批評（VULNERABLE）を踏まえ #9 を Already → Gap に格上げ
- Gemini 警告（個人 dotfiles で drift 頻発リスク）を踏まえ snapshot detection scope を single-run 内に限定
- Token strip は最低優先（Codex 批評）。playbook 記述レベルに留め、wrapper script 実装は別タスク
- 実装順序は F0 → #9+#10 → #13+#11（Codex 推奨: 既存 Follow-Ups 消化を最優先）
