# System Prompt Patcher

Claude Code CLI のバンドルに含まれるシステムプロンプトから、不要・冗長なセクションを削除するパッチシステム。

## 背景

Claude Code は起動時にシステムプロンプトをバンドルから読み込む。
プロンプト中には、ユーザーが CLAUDE.md で既にカスタマイズ済みのセクションや、
不要な定型文が含まれており、コンテキストウィンドウを無駄に消費する。

このツールは [ykdojo/claude-code-tips (Tip 15)](https://github.com/ykdojo/claude-code-tips) に基づき、
バンドル内のシステムプロンプトを安全にパッチして不要部分を除去する。

## 仕組み

1. `npm root -g` で Claude Code のグローバルインストール先を特定
2. バンドルファイル（`cli.mjs` / `cli.js`）を検出
3. `patches/{versionBucket}/` 内の `.find.txt` / `.replace.txt` ペアを読み込み
4. Variable-aware regex でミニファイされた変数名の差異を吸収しつつパッチ適用
5. バックアップ（`.bak`）を作成してからパッチを書き込み

### バージョンバケット

Claude Code のバージョン `2.1.76` → `2.1.x` のようにパッチバージョンを切り捨てて
マイナーバージョン単位でパッチを管理する。これにより、パッチバージョン更新のたびに
パッチファイルを更新する手間を軽減できる。

## 使い方

```bash
# パッチ適用
node tools/system-prompt-patcher/patch-cli.js

# パッチ後の検証
node tools/system-prompt-patcher/verify-patch.js

# バックアップから復元（手動）
# verify-patch.js が失敗時に自動復元するが、手動でも可能:
# cp <bundle>.bak <bundle>
```

## パッチ作成方法

1. `patches/` の下にバージョンバケットのディレクトリを作成（例: `patches/2.2.x/`）
2. 削除したいセクションを `001-section-name.find.txt` に記述
3. 置換後の内容（空文字なら空ファイル）を `001-section-name.replace.txt` に記述
4. find テキスト中の変数名は `{{VAR}}` プレースホルダーで記述可能（regex `\w+` に展開される）

### パッチファイル命名規則

```
{番号}-{説明}.find.txt     # 検索対象テキスト
{番号}-{説明}.replace.txt  # 置換テキスト（空ファイル = 削除）
```

番号は適用順序を制御する（昇順）。

## 参考リンク

- [ykdojo/claude-code-tips](https://github.com/ykdojo/claude-code-tips) — Tip 15: System Prompt Optimization
- [Anthropic Claude Code Docs](https://docs.anthropic.com/en/docs/claude-code)
