# Codex Long-Horizon Workflow

`dotfiles` で Codex を単発の補助ではなく、調査・実装・検証を反復する agent として使うための運用メモ。

## Goal

この workflow の目的は、macOS dotfiles の設定変更を安全に進めること。
単発のコード生成ではなく、調査・計画・実装・検証を反復しながら完了まで進める。

## Repo Context

- この repo は `~/.config`、`~/.claude`、`~/.codex` に symlink される設定の実体を管理する
- 変更は最小限にする
- 既存の命名規則、構成、ツール選定に従う
- README と実ファイルの整合を保つ
- 無関係な設定は触らない

## Inputs

- 対象
  - 例: `wezterm`, `zsh`, `aerospace`, `claude`, `codex`
- 要求
  - 何を改善したいか
- 制約
  - 壊してはいけない挙動
  - 維持したい UX
  - 既存キーバインドや互換性
- 完了条件
  - 何が変われば成功か

## Working Rules

- 最初に関連ファイル、README、既存設定を調査する
- 調査だけで結論を出さず、必要なら小さく実装して検証する
- 変更後は必ず対象に近い検証を実行する
- 破壊的変更や広範囲変更は approval 前提で扱う
- 推測で完了宣言しない
- main thread は requirements、decision、final output に寄せる
- 並列に進める探索、代替案、要約作成は必要に応じて worktree や subagent に分離する

## Parallel Surfaces

長時間 task では、並列化の価値は速度だけでなく context 分離にある。

- 同一 project 内の別 thread
  - debugging、alternative exploration、summary を 1 本の流れに潰さず、目的ごとに分ける
- worktree
  - foreground の main workspace と衝突させたくない代替案、長時間試行、破壊的寄りの実験を逃がす
- subagent
  - 影響範囲調査、review、docs/config 確認のような read-heavy task を main thread から切り離す

判断基準:

- 今の判断と編集に直結するものは foreground
- 比較対象、探索ノイズ、長時間試行は background

## Standard Loop

### 1. Read

- 関連する設定ファイル
- 対応する `README.md`
- 既存の task や script

### 2. Plan

- 変更点を 3 個以内に要約
- 影響範囲を明示
- 検証方法を先に決める

### 3. Implement

- 最小差分で変更する
- 既存パターンを優先する
- 新しい抽象化は必要な場合のみ導入する

### 4. Verify

必要に応じて以下を実行する。

- `task validate`
- `task validate-configs`
- `task validate-readmes`
- `task validate-symlinks`
- `task symlink`
- `task restart-wm`
- その他、対象固有の確認コマンド

失敗したら修正して再検証する。

### 5. Summarize

最後は以下をまとめる。

- 原因
- 修正内容
- 効果
- 実行した検証
- 未確認事項

## Milestone Strategy

大きい変更は milestone 単位で進める。

### Milestone 1: Baseline

- 現状把握
- 問題の再現
- 変更対象の限定

### Milestone 2: Safe Change

- 小さい差分で改善
- 既存挙動を壊さないことを優先

### Milestone 3: Validation

- `task validate` 系を実行
- 必要なら対象ツールの再読込や再起動を実施

### Milestone 4: Cleanup

- README と設定の整合確認
- 不要差分がないか確認

## Approval Policy

次は approval 前提で扱う。

- `rm`, `git reset`, `git checkout --` などの破壊的操作
- 大量ファイル変更
- 外部ネットワーク依存の導入
- OS 状態を大きく変えるコマンド

## Recommended Profiles

- 軽い修正: `codex --profile fast`
- レビューや整理: `codex --profile review`
- 調査や比較: `codex --profile research`

## Reusable Skills

必要なら以下を `@.../SKILL.md` で参照してよい。

- `@.config/claude/skills/frontend-design/SKILL.md`
- `@.config/claude/skills/react-best-practices/SKILL.md`
- `@.config/claude/skills/senior-architect/SKILL.md`
- `@.config/claude/skills/senior-backend/SKILL.md`
- `@.config/claude/skills/senior-frontend/SKILL.md`

`SKILL.md` が `references/` を参照している場合は、必要なファイルだけ追加で `@` 参照する。

## Prompt Template

```md
この repo の dotfiles workflow に従って作業してください。

対象: <tool or directory>
目的: <what to improve>
制約:
- <must keep>
- <must not break>
完了条件:
- <definition of done>

進め方:
- まず関連ファイルと README を調査
- 変更計画を短く示す
- 実装
- `task validate` か対象に近い検証を実行
- 最後に 原因 / 修正内容 / 効果 / 検証結果 を報告
```

## Output Format

最後は必ず以下で報告する。

- 原因
- 修正内容
- 効果
- 検証結果
- 残課題
