# Starship プロンプトの Nerd Font アイコン修正

## 問題

Starship の各言語モジュールで:
- `via` というテキストが表示される（format 未指定時のデフォルト）
- アイコンが表示されない（Unicode 文字がスペースに化けている）

## 原因

1. `format` が未指定だとデフォルトで `via $symbol($version)` になる
2. TOML ファイル内のシンボル文字が保存時に空白（U+0020）に化けていた

## 修正方法

### format の明示指定

各言語モジュールに `via` を含まない format を追加:

```toml
[nodejs]
format = '[$symbol($version )]($style)'
```

### アイコン文字の正しい書き込み

エディタによっては Nerd Font の文字が正しく保存されない場合がある。
Python で正しい Unicode コードポイントを直接書き込む:

```python
import re

with open('.config/starship.toml', 'r') as f:
    content = f.read()

# \uXXXX エスケープを実際の Unicode 文字に変換
content = re.sub(
    r'\\u([0-9a-fA-F]{4})',
    lambda m: chr(int(m.group(1), 16)),
    content
)

with open('.config/starship.toml', 'w') as f:
    f.write(content)
```

### 検証方法

```python
python3 -c "
with open('.config/starship.toml') as f:
    for line in f:
        if 'symbol' in line and '=' in line:
            val = line.split('=', 1)[1].strip().strip(\"'\").strip('\"')
            hexes = ' '.join(f'U+{ord(c):04X}' for c in val)
            print(f'{hexes}')
"
```

アイコンが `U+0020` だけなら壊れている。正しい例: `U+E718 U+0020`

## 各モジュールのアイコン一覧

| モジュール | コードポイント | 用途 |
|-----------|---------------|------|
| git_branch | U+E725 | Git ブランチ |
| python | U+E73C | Python |
| lua | U+E620 | Lua |
| nodejs | U+E718 | Node.js |
| golang | U+E626 | Go |
| haskell | U+E777 | Haskell |
| rust | U+E7A8 | Rust |
| ruby | U+E791 | Ruby |
| aws | U+E7AD | AWS |
| docker | U+F308 | Docker |
| jobs | U+F013 | バックグラウンドジョブ |

## 前提

WezTerm で Nerd Font 対応フォントを使用していること:

```lua
font = wezterm.font_with_fallback({
  "Hack Nerd Font",
  "HackGen Console NF",
})
```
