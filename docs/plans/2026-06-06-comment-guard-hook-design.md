# comment-guard hook 設計メモ

- **日付**: 2026-06-06
- **状態**: 実装完了（2026-06-06、hook + test 27ケースPASS + settings.json 配線 + .gitignore）。/review PASS（Codex CLI は stdin hang で Haiku fallback）
- **規模**: M（新規 hook 追加 = harness 変更）
- **由来**: grill-me インタビューで設計確定。当初要望「コメントを見直す＋修正する Skill」→ MH4GF `comment-guard.sh`（`MH4GF/claude-code` repo, `user-scope/hooks/comment-guard.sh`, MIT License）参照を経て「予防 hook 特化」に収束。

## 目的

私（Claude）が低価値なコードコメントを乱造するのを **予防** する。
コメントはデフォルト禁止とし、価値ある **Tier 1（ハザード/制約 = 「そうしないと何が起きるか」）** だけを意識的 override で書かせる。

> ユーザーのコメント哲学: 作業経過や「なぜそうしたか（意図）」より、「そうしないと何が起きるか（結果・ハザード・制約）」を重視。経緯・意図は git commit message に置く。

## コメントの価値序列（Tier）

設計判断の背骨。ただし **hook 自身は Tier を判定しない**（鈍いまま）。Tier は deny メッセージのガイドと人間 override 判断に効く。

| Tier | 内容 | 扱い |
|---|---|---|
| 1 | ハザード/制約（「逆順だと deadlock」「0 を null 扱いで残高消失」） | 最も価値が高い。書くなら意識的 override |
| 2 | 非自明な WHY（意図） | 可能なら Tier 1（結果ベース）へ昇格させて書く |
| 3 | 作業経過・履歴（「5月に田中追加」「前はループだった」） | 不要。commit message へ |
| 4 | 自明コメント（`i++ // i をインクリメント`） | 不要 |

## アーキテクチャ決定

| 項目 | 決定 | 理由 |
|---|---|---|
| 形態 | **hook のみ**（PreToolUse deny）。skill は作らない | 「hook 特化」。treatment（見直す＋修正）は YAGNI 保留、低品質が出たら iterate |
| ベース | MH4GF `comment-guard.sh` を **adapt** | 実証済み awk ロジック再利用。要ライセンス確認＋ attribution コメント |
| 判定 | pragma 以外の **コメント純増を全 deny**（blunt）。fail-open | Tier 判定を hook に持ち込むと determinism boundary を壊す。「鈍いまま」が設計上の必然 |
| Tier 哲学との整合 | 良い Tier 1 コメントも block される = 機能であって欠陥でない | 高価値コメントは稀であるべき。override の一手間が乱造の防波堤 |
| 対象拡張子 | `ts tsx js jsx mjs cjs go rs` / `json` / `yaml yml py` / `sql` | MH4GF ＋ rust。**shell 除外**（dotfiles ハーネススクリプトは説明コメントが正当に価値を持つ。`comment-guard.sh` 自身の冒頭コメントが Tier 1 の好例。「ゲート/フックは冗長性必須」と自己矛盾するため） |
| 範囲 | グローバル・**デフォルト ON**・dotfiles で git 管理 | 「どこでも低価値コメントを書かせたくない」の素直な実装。仕事リポジトリ（hearable 等）でも発火する点は承知のうえ、env で個別 OFF |

## 逃げ道（escape hatch）

skill を作らないので、marker を touch する主体は「私が Bash で明示」or「ユーザー手動」になる。

1. **`COMMENT_GUARD=off` 環境変数** — セッション全体キルスイッチ（dotfiles でコメント作業する時など）
2. **marker `.claude/tmp/.comment-guard-allow`**（30分有効、自然失効）— 私が Bash で `touch` する or ユーザー手動。Bash touch は tool call として **可視・監査可能**（こっそりバイパス不可）
3. 人間ステアのフロー: 私が Tier 1 コメントを書きたい → ユーザーに「このハザードコメント書きたい、override していい？」と確認 → 承認後 touch して書く

## deny メッセージ（案）

> 新規コードコメントの追加はブロックされています。**経緯・意図は git commit message に書いてください**。コードに残すなら「そうしないと何が起きるか（ハザード・制約）」を書く Tier 1 コメントに限り、その場合はユーザーに確認のうえ override（`COMMENT_GUARD=off` または marker touch）してください。

## 配置

| 対象 | パス |
|---|---|
| hook script | `.config/claude/scripts/policy/comment-guard.sh` |
| 登録 | `.config/claude/settings.json` の `PreToolUse`（matcher = `Edit\|Write\|MultiEdit`） |
| marker | `.claude/tmp/.comment-guard-allow`（**gitignore 対象**、git 管理しない） |

## hook ロジック（MH4GF 踏襲）

- 入力 JSON から `tool_name` を読み、Edit/Write/MultiEdit のみ処理（他は exit 0）
- `file_path` の拡張子で family 判定（c-family / hash / sql）。対象外拡張子は exit 0
- `count_comments`: family ごとに文字列リテラルを除去してからコメント行をカウント。pragma（`eslint-` `@ts-` `biome-ignore` `# noqa` `# type:` `//go:` `prettier-ignore` 等）は allowlist で除外
- `contribution`: old/new のコメント数の差分。c-family はバッククォート奇数（テンプレートリテラル途中）、hash は YAML ブロックスカラー（`|` `>`）で誤検知回避 → 0 を返す
  - **既知の制限（fail-safe 側）**: YAML ブロックスカラーガードは `new` 全体で判定するため、同一 edit 内に `run: |` とコメント追加が混在すると、その edit のコメント増分は丸ごとスキップされ allow になる（false-negative）。allow 方向（=編集を止めない）に倒れる安全側の割り切り。同一 edit で block scalar とコメント追加が同時に起きるケースは稀。
- 純増（total > 0）かつ marker 不在/失効 → **deny**。それ以外は exit 0（allow）
- fail-open: 判定不能・jq エラー等はすべて exit 0

## 実装時の義務（CLAUDE.md ハーネス規約）

- ハーネス変更 → **Codex Review Gate（codex-reviewer + code-reviewer 並列）＋ `/review` PASS が mandatory**
- 最低検証: `task validate-configs`, `task validate-symlinks`
- `settings.json` 追加前に **既存 `PreToolUse` 配列を grep**（重複登録防止 — `feedback_settings_json_grep_first`）
- hook 単体テスト:
  - コメント純増の Edit JSON を流して `permissionDecision: deny` が出ること
  - pragma 行（`// eslint-disable` 等）が通ること
  - 対象外拡張子（`.md` 等）で exit 0 すること
  - marker 存在時に allow されること
  - `COMMENT_GUARD=off` で exit 0 すること

## 保留した範囲（将来 iterate 候補）

- **treatment skill**（既存・人間記述・hook 導入前コメントを Tier 序列で見直す＋修正、Tier 2→1 昇格）。当初要望だが YAGNI で保留。「低品質コメントが出てきたら改善を加える」方針
- hook を賢くする（ハザードキーワード allowlist 等）案は **却下**。determinism boundary を崩すため
