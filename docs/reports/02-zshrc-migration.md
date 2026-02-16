# .zshrc の移行とローカル設定の分離

## 概要

既存の `~/.zshrc`（実ファイル）を dotfiles 管理の symlink に置き換え、
マシン固有の設定は `local.zsh` に分離する。

## 構成

```
~/.zshrc → ~/dotfiles/.zshrc (symlink)
           ↓ source
~/.config/zsh/.zshrc          # メイン設定（自動で core/, tools/ 等を読み込み）
~/.config/zsh/local.zsh       # マシン固有設定（gitignore 済み）
```

## 手順

### 1. 既存 .zshrc の内容を確認

```bash
cat ~/.zshrc
```

dotfiles 側でカバーされている設定を確認:
- Docker completions → `tools/docker.zsh`
- mise activate → `tools/mise.zsh`
- PATH 設定 → `core/path.zsh`
- Go PATH → `core/env.zsh` + `core/path.zsh`

### 2. マシン固有の設定を local.zsh に移動

API キーやプロジェクト固有の環境変数など、リポジトリに含めたくないもの:

```bash
# ~/.config/zsh/local.zsh の例
export GOOGLE_GENAI_USE_VERTEXAI=true
export GOOGLE_CLOUD_PROJECT=your-project
export GOOGLE_CLOUD_LOCATION=us-central1
```

### 3. .zshrc を symlink に置換

```bash
rm ~/.zshrc
ln -s ~/dotfiles/.zshrc ~/.zshrc
```

以降は `symlink.sh` が自動管理する。

### 4. 反映

```bash
exec zsh
```

## local.zsh について

- `.config/zsh/.zshrc` の末尾で `[[ -f "$ZSHDIR/local.zsh" ]] && source` される
- `.gitignore` に `.config/zsh/local.zsh` を追加済み
- 新しいマシンでは手動で `local.zsh` を作成する必要がある
