---
name: careful
description: >
  Use when working near production systems or performing potentially destructive operations.
  Prompts for confirmation on every Bash command via a session-scoped PreToolUse guard.
  Triggers: 'careful', 'prod操作', '本番', 'production', '慎重モード'.
  Do NOT use for: normal development — overhead is too high for routine work.
origin: self
metadata:
  pattern: guard
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: prompt
          prompt: >
            [CAREFUL MODE] 破壊的操作の可能性を検出しました。
            本番環境に影響する可能性があります。以下を確認してください:
            1. 対象が正しい環境か（dev/staging/prod）
            2. ロールバック手段があるか
            3. 影響範囲を把握しているか
            本当に実行しますか？
---

# /careful — 破壊的操作ガードモード

本番環境やクリティカルな操作を行う際の安全装置。
スキル起動中は **すべての Bash コマンド** に対して確認プロンプトが表示されます。

## Usage

```
/careful
```

セッション中有効。通常の開発作業では使わないこと（毎回確認が入るためオーバーヘッドが大きい）。

## When to Use

- 本番DBへの直接操作
- kubectl で本番クラスタを操作
- git push --force を行う可能性がある作業
- rm -rf で重要ディレクトリを操作
- 環境変数や secrets の変更

## How It Works

PreToolUse フックで Bash ツール呼び出しをインターセプトし、
実行前に環境確認・影響範囲確認・ロールバック手段の確認を促します。

## Gotchas

- **hard block ではない**: `type: prompt` なので「はい」で通る。コマンド判別もしないため `rm -rf` 等を名指しで検出しているわけではない
- **決定論的に止まるものと止まらないもの**: `rm -rf` / `git push --force` は settings.json の deny で実際にブロックされる。一方 **`kubectl delete` と `DROP TABLE` はどこにも deny ルールがなく、この確認プロンプトが唯一の防波堤**（SQL 文は glob で捕まえにくいため deny 追加自体が難しい）。deny に足せるものは足す、足せないものはここに書いて明示する
- **オーバーヘッド**: 全 Bash コマンドに確認が入る。通常開発では使わない
- **Read 系は対象外**: Read, Grep, Glob はブロックしない（読み取りは安全）
- **セッション限定**: スキル起動セッション中のみ有効。新セッションでは再起動が必要
