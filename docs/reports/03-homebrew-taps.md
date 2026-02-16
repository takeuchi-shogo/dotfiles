# Homebrew サードパーティ Tap

## 概要

一部ツールは Homebrew 標準リポジトリに含まれないため、
サードパーティ tap の追加が必要。

## 必要な Tap

| Tap | 提供するパッケージ |
|-----|-------------------|
| `FelixKratz/formulae` | sketchybar, borders |
| `nikitabobko/tap` | aerospace (cask) |

## Brewfile での定義

```ruby
# Taps
tap "FelixKratz/formulae"
tap "nikitabobko/tap"

# これにより以下が利用可能
brew "sketchybar"
brew "borders"
cask "aerospace"
```

## 手動インストール

tap が失敗した場合:

```bash
brew tap FelixKratz/formulae
brew tap nikitabobko/tap

brew install sketchybar borders
brew install --cask nikitabobko/tap/aerospace
```

## サービス起動

```bash
brew services start sketchybar
brew services start borders
open -a AeroSpace
```
