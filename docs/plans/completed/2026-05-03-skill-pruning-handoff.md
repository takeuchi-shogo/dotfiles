---
status: paused
paused_reason: "settings.json 配線完了。残 1 件は数日運用検証 (時間経過待ち)"
created: 2026-05-03
last_updated: 2026-05-03
session_id: 718efc7a-e3ad-46cb-bb1b-e0d573648e51
type: handoff
---

# Skill Pruning + Harness Cleanup — Handoff

## Why this exists

ユーザーが「skill モリモリすぎて読めない」「整理を /improve でやりたかったが機能してなかった」と発言。
4 セッション (2026-04-30 〜 2026-05-03) かけて以下を実施:

1. **AutoEvolve / `/improve` の根本問題を ultrathink で診断** (Sonnet + Codex 並列)
2. **22 skill を retire** (Sonnet 判定 + Codex 独立精査の統合)
3. **削除 skill への dangling pointer を 20+ ファイル整理**
4. **AutoEvolve ecosystem に deprecation 注記** (script は keep、policy/artifacts のみ legacy)
5. **daily-report skill を再設計** (sessions-index.json 3ヶ月停止問題を bypass)
6. **conventional-commit hook の emoji drift 解消** (gitmoji 5 個追加)
7. **Harness Review Gate を session-aware 化** (並行 5 session で false-positive 4 回検出への対処)

## Goal (Definition of Done)

### Agent 完了 (本セッションで完結)
- [x] skill 数を 130 → 108 に削減 (▲22)
- [x] retire skill への active な dangling reference を 0 件に
- [x] daily-report が動く状態に (sessions-index.json 依存解消)
- [x] commit-msg hook で `🔥 fix` 等が通る
- [x] 並行 session で他 session の harness 編集が trigger しない (script レベル)
- [x] **handoff document 作成** (本ファイル、resume 用 context 完備)

### User Action 待ち (agent 権限外)
- [x] **settings.json への harness-snapshot.py 配線** (2026-05-03 14:27 完了、手動実行で snapshot 生成確認済)
- [ ] 数日運用で動作確認 (時間経過待ち)
  - → 詳細: 下記「数日運用後の verification」セクション

## Completed (10 commits)

| # | Commit | 内容 | 規模 |
|---|---|---|---|
| 1 | `6478b01` | 6 skills retire (1st wave) | -1,504 行 |
| 2 | `8775fd8` | 16 skills retire (2nd wave + Codex 統合) | -3,343 行 |
| 3 | `ea603f5` | 11 dangling refs cleanup (active scope) | -42 net |
| 4 | `68c3b5e` | 9 dangling refs (/epd, /memory-status 等) | -13 net |
| 5 | `70695e1` | improve-policy + autoevolve-artifacts deprecated 注記 | +18/-8 |
| 6 | `2e1c00c` | daily-report Step 2 jsonl 直読み | +46/-21 |
| 7 | `fa15675` | conventional-commit hook に gitmoji 5 個追加 | +6/-1 |
| 8 | `c07cf71` | feature-tracker AutoEvolve 連携 stale 注記 | +3/-2 |
| 9 | `07a5d67` | Harness Review Gate session-aware (false-positive 解消) | +111/-2 |

(commit 1 は前セッション、2-9 は 2026-05-03)

## Retired skills (22 個)

### 1st wave (6, commit `6478b01`)
- senior-backend, codex-review, senior-frontend, obsidian-content, continuous-learning, verification-before-completion

### 2nd wave (16, commit `8775fd8`)
- improve, persona, dev-ops-setup, kanban, capture, morning, meeting-minutes, dev-insights, dev-cycle, epd, nano-banana, upload-image-to-pr, quiz, memory-status, profile-drip, interview

## Probation (6 個 — Codex 推奨で 30日 keep、再評価へ)

呼ばれなければ次回 retire 候補:
- autonomous, graphql-expert, buf-protobuf, prompt-review, difit, refactor-session

## Critical: ユーザー手動依頼

### settings.json への hook 配線 (1 件)

**Permission deny で自動配線不可。手動で実行**:

`~/.claude/settings.json` の `hooks.SessionStart` 配列、`memory-integrity-check.py` entry の直後に追加:

```json
{
  "hooks": [
    {
      "type": "command",
      "command": "python3 $HOME/.claude/scripts/runtime/harness-snapshot.py",
      "timeout": 5
    }
  ]
}
```

これがないと **harness-snapshot は生成されず、Harness Review Gate session-aware 化が機能しない** (並行 session false-positive が再発)。

実行コマンド (lefthook 経由でない場合):
```bash
# 編集後に validity 確認
python3 -c "import json; json.load(open('/Users/takeuchishougo/.claude/settings.json')); print('VALID')"
```

## 数日運用後の verification

新セッションを 1 つ起動して以下を確認:

```bash
# 1. harness-snapshot が生成される
ls ~/.claude/session-state/initial-harness-*.txt

# 2. Harness Review Gate false-positive 解消
#    並行 session で他 session の harness 編集が Stop hook で block されない
#    (本セッション中に編集していない skill ファイルは無視される)

# 3. daily-report 動作
/daily-report yesterday
ls ~/daily-reports/

# 4. emoji hook 動作
git commit -m "🚑 fix(test): hotfix"  # 通る
git commit -m "💄 style(test): polish"  # 通る

# 5. skill 整理効果
ls -d ~/.claude/skills/*/ | wc -l  # 108 を確認
```

## Resume 用 context

### 次回セッションで継続する場合

このファイル (`docs/plans/active/2026-05-03-skill-pruning-handoff.md`) を Read してから以下を確認:

1. **git log -10 --oneline**: 上記 commit が反映されているか
2. **settings.json の SessionStart hook**: harness-snapshot.py が wired されているか
3. **未完了タスク (Goal の checkbox)**: ✓ がついていないものに着手

### 関連ファイルのスナップショット

#### 削除した skill (22 個) の確認用 grep
```bash
for skill in improve persona dev-ops-setup kanban capture morning meeting-minutes dev-insights dev-cycle epd nano-banana upload-image-to-pr quiz memory-status profile-drip interview senior-backend codex-review senior-frontend obsidian-content continuous-learning verification-before-completion; do
  [ -d ~/.claude/skills/$skill ] && echo "残存: $skill"
done
```

(何も出なければ全削除済み)

#### Probation skill の使用状況確認
```bash
python3 -c "
import json, os, collections
counter = collections.Counter()
with open(os.path.expanduser('~/.claude/agent-memory/learnings/skill-executions.jsonl')) as f:
    for line in f:
        try:
            d = json.loads(line)
            n = d.get('skill_name', '')
            if n: counter[n] += 1
        except: pass
for skill in ['autonomous', 'graphql-expert', 'buf-protobuf', 'prompt-review', 'difit', 'refactor-session']:
    print(f'  {skill}: {counter.get(skill, 0)} calls')
"
```

## 既知の制約 (Permission boundary)

このセッション中に以下が permission deny された:
- **settings.json への hook 追加** (前セッションで「今回限り」revert した文脈で boundary 残留)
- 他のユーザー編集 (auto mode 関連) は revert 済み

## Out of scope (β phase / 別 task)

Codex 指摘で別 task 推奨されたもの:

### Phase 3-A.β: AutoEvolve script の整理 (大規模、未着手)
- `scripts/learner/` (15+ files) の AutoEvolve specific 部分削除
- `scripts/lib/session_events.py` は **絶対残す** (Rust hooks の telemetry emit 中核)
- `references/improve-policy.md` etc は完全 retire か (今回は legacy 注記のみ)
- 意思決定が前段: 「AutoEvolve を完全廃止か復活余地を残すか」

### その他
- **observability producer dead** (errors.jsonl 16d / friction-events 25d 0 emit) は ultrathink セッションで「producer 死亡ではなく検出条件が investigation 中心の使い方では発火しない設計」と判明。修正不要、producer 健全
- **/improve 自体の再設計** (skill curator として作り直す案) は user が判断する話
- **agents/autoevolve-core.md** は legacy 注記済、scripts 連携保守のため削除は見送り

## Decision log (このセッションの主要判断)

| 判断 | 理由 |
|---|---|
| Codex に独立精査依頼 | Self-preference bias 回避、Sonnet が見落とした 7 点を Codex が指摘 |
| dev-ops 系 7 個一括 retire | 互いに `/dev-ops.local.json` 設定依存、運用していないため一括判断 |
| autoevolve-core agent は legacy 注記のみ | scripts/learner との連携保守、scripts 整理は別 task |
| settings.json の SessionStart hook 配線は手動依頼 | permission deny、user policy 尊重 |
| EPD section 全削除 + section 番号 shift | `/epd` retire に伴い workflow document も整合 |

## Reference: 関連 commit hash

```
07a5d67 ✨ feat(harness-gate): make Harness Review Gate session-aware
c07cf71 🔧 chore(feature-tracker): note that AutoEvolve consumer was retired
fa15675 🔥 fix(commit-msg-hook): allow gitmoji removal/breaking/critical emojis
2e1c00c ✨ feat(daily-report): rewrite Step 2 to use jsonl direct walk
70695e1 🔧 chore(autoevolve): mark improve-policy and artifacts as deprecated
68c3b5e 🔧 chore(harness): clean up remaining /epd and legacy refs
ea603f5 🔧 chore(harness): clean up dangling references to retired skills
8775fd8 🔧 chore(skills): retire 16 unused or redundant skills second wave
6478b01 🔧 chore(skills): retire 6 unused self-made skills (前セッション)
```

---

**Status**: settings.json 手動配線 + 数日運用検証待ち。それ以外は完了。
