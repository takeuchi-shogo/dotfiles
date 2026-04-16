# Session Protocol

セッション境界を明確にし、マルチセッション開発の一貫性を保つプロトコル。

## Session Start Protocol

セッション開始時に `session-load.js` が自動実行する項目:

1. **前セッション状態の復元** — `last-session.json` or `HANDOFF.md`
2. **アクティブプラン確認** — `docs/plans/active/`, `tmp/plans/`
3. **Feature List 確認** — `feature_list.json` が存在すれば次の未完了機能を表示
4. **Progress Log 確認** — `progress.log` が存在すれば直近エントリを表示
5. **テストベースライン** — テストランナー検出と実行提案
6. **Learnings ロード** — タスク関連の過去の学びを表示

## Session End: Clean State Definition

セッション終了時に目指す状態（**main マージ可能レベル**）:

- [ ] `git status` がクリーン（uncommitted changes なし）
- [ ] テストが全パス
- [ ] `feature_list.json` の `passes` 状態が実際のテスト結果と一致
- [ ] `progress.log` にセッションの作業内容が記録済み
- [ ] `HANDOFF.md` が不要（全作業がコミット済み）

`completion-gate.py` が上記を advisory（警告のみ）でチェックする。

### Blast Radius クリーンアップ（L タスクのセッション終了時）

L タスクのセッション終了時は、変更の影響範囲を確認してエントロピー増大を防ぐ:

- **ドキュメント同期**: 変更した関数・API の挙動が既存ドキュメントに反映されているか（`doc-gardener` agent）
- **影響範囲確認**: 変更が他ファイルのインターフェースを壊していないか（`cross-file-reviewer` agent）
- **矛盾解消**: 古い挙動を参照する記述が残っていないか

> Ref: OpenForage "Entropy Maximization" — エージェントは自分が変更したコード以外のドキュメント同期を行わない。100回繰り返すとメンテ不能なリポジトリになる

## State Persistence: 棲み分け

| 仕組み | スコープ | 寿命 | 用途 |
|--------|----------|------|------|
| **memory** (MEMORY.md) | グローバル / プロジェクト | 永続 | セッション横断の学び・パターン |
| **progress.log** | プロジェクト固有 | プロジェクト寿命 | 時系列の作業ファクト記録 |
| **checkpoint** | セッション | 短期（5世代保持） | セッション再開用の runtime state |
| **HANDOFF.md** | セッション間 | 次セッションまで | セッション引き継ぎの作業コンテキスト + 失敗アプローチ記録 |
| **feature_list.json** | プロジェクト固有 | プロジェクト寿命 | 機能単位の構造化進捗管理 |
| **Plan** (docs/plans/) | プロジェクト固有 | タスク寿命 | Goal/Scope/Validation/Decision の記録 |

## Dead-End Prevention (失敗アプローチ記録)

> Ref: "Long-Running Claude" — "Without them, successive sessions will re-attempt the same dead ends."

セッション跨ぎの長時間タスクでは、失敗したアプローチを構造的に記録する:

1. **記録場所**: `HANDOFF.md` の「3.5. 失敗したアプローチ (Dead Ends)」セクション
2. **記録タイミング**: アプローチを試して失敗した直後（記憶が新鮮なうちに）
3. **必須項目**: アプローチ名、失敗理由、次セッションへの学び
4. **セッション開始時**: `HANDOFF.md` の Dead Ends セクションを必ず確認し、同じアプローチを再試行しない

## Session Granularity Rules

`feature_list.json` が存在する L 規模プロジェクトでは:

- **1 セッション 1 機能** に集中する
- 同一セッションで複数機能を完了させない（コンテキスト喪失のリスク）
- S/M 規模タスクにはこのルールを適用しない（過剰制約を避ける）
- `completion-gate.py` が 2 機能以上の同時完了を検出した場合、警告を出す

## Compact vs Clear Decision Matrix

> 出典: Anthropic "Using Claude Code: Session Management & 1M Context" (2026-04) — `/compact` (lossy auto-summary, steering 可) と `/clear` (自作 distilled brief + 新セッション) のトレードオフ。

長セッションでコンテキストを軽量化する2手段の使い分け:

| 判断軸 | `/compact {steering}` | `/clear` + 自作 brief |
|--------|----------------------|----------------------|
| **方向性** | 直後も同方向のタスクを継続 | 方向転換、または関連度の低い次タスク |
| **Context rot** | まだ感じていない（compaction 1-2回目） | 感じている（同質問の繰り返し、Plan 逸脱、compaction 3回超） |
| **重要情報の再取得コスト** | 高い（多数のファイルを再読する必要がある） | 低い（重要ファイルは brief に書き起こせる） |
| **ユーザーのコスト** | 低い（自動要約に任せる） | 高い（自分で brief を書く） |
| **出力品質** | モデル任せ（lossy、セマンティックドリフトのリスク）| 自分で取捨選択（意図が残る）|
| **dotfiles での代替** | `pre-compact-save.js` が git 状態・Plan を自動保存 + `compact-instructions.md` の保留優先度で品質を補強 | `/checkpoint` で HANDOFF.md + RUNNING_BRIEF.md 生成 → 新セッション |

### Bad Compact の兆候と回避

> 記事の知見: モデルが次の方向を予測できない時に autocompact が発動すると重要情報が欠落する。debugging セッション直後に autocompact → 次ターンで「別ファイルの warning を直して」と指示 → warning の情報が summary から落ちていて誤動作、等。

**回避策（優先順）:**

1. **autocompact を待たず proactive に `/compact {focus}` を発動**: 次にやりたいことを明示する (`/compact focus on auth refactor, drop test debugging`)
2. **方向転換時は `/compact` ではなく `/clear` を選ぶ**: モデルが方向を予測できない状態での compact は品質が最低
3. **compaction 3回超えたら迷わず `/clear`**: `context-compaction-policy.md` の Reset > Compaction 原則と整合

### 判断フロー

```
新しいターンを送る前に状況を評価:
├─ 次タスクが現セッションと同方向?
│   └─ Yes → /compact {focus-instruction} で steering
│   └─ No  → /clear + 自作 brief で新セッション
└─ context rot や bad compact の兆候あり?
    └─ Yes → 即 /clear（compact は品質劣化を悪化させる）
```
