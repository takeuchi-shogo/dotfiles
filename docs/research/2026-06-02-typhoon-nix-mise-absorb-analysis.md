---
source: "https://qiita.com/tyPhoon/items/f1855ff508f4268df5b5"
date: 2026-06-02
status: partially-implemented
topic-family: "nix-mise-dotfiles-environment (新分野, N=1)"
---

## Source

- **URL**: https://qiita.com/tyPhoon/items/f1855ff508f4268df5b5
- **タイトル**: 私の最強のMac開発環境 2026: Nixとmiseで育てる
- **著者**: tyPhoon (株式会社nekonata), 2026-05-29
- **取得**: obsidian:defuddle (Qiita は trusted 外のため)

## 記事の主張

Mac 開発環境を3層で役割分担すると再現性と身軽さが両立する。

- **Nix/home-manager/nix-darwin**: OS全体の土台(シェル/エディタ/CLI/設定配布/macOS設定)
- **Homebrew**: TCC権限の都合でNixと相性が悪いGUIアプリ本体
- **mise**: プロジェクトごと/更新頻度の高い開発者ツール(Node/Go/Java/uv/just/lefthook/Codex)

core(共通)とdotfiles(マシン固有)の2層リポ分離も提唱。

## Gap Analysis (Pass 1: 存在チェック)

| 手法 | 判定 | 詳細 |
|------|------|------|
| Nix土台(nix-darwin+home-manager) | Already | Phase B2完了, private/work マルチホスト構成済み |
| Homebrew GUI 役割分担 | Already | cask 管理済み |
| 役割分担思想(Nix/brew/mise) | Already | 中核思想は既実装 |
| AeroSpace+workspace固定 | Already | 設定済み |
| borders | Already | 設定済み |
| Ghostty | Already | 使用中 |
| Yazi | Already | 設定済み |
| Karabiner | Already | 設定済み |
| jj+lazygit+lazyjj | Already | 設定済み |
| direnv | Already | 設定済み |
| zoxide | Already | 設定済み |
| bat | Already | 設定済み |
| eza | Already | 設定済み |
| starship | Already | 設定済み |
| mise でランタイム管理 | Partial→Gap(中核) | mise 本体+多数のツール(buf/dart/deno/flutter/go複数版/java/kubectl等)はinstall済・activate済だが、グローバルconfigに`[tools]`が無く**グローバル有効化ゼロ**(`mise current`空)。ルートの.tool-versionsも無い |
| carapace | Gap(小) | 未導入 |
| espanso | Gap(小) | cask 宣言のみ、設定なし |
| Nixvim化 | Partial | 非推奨, 大作業で利得小 |
| core/dotfiles 2層分離 | N/A | 個人1リポでYAGNI |
| Nushell/Zellij | N/A | zsh/cmux+tmux で代替済み |

## 重大な発見

1. **mise はツール install 済みだがグローバル有効化ゼロ** (当初「未運用」と判定したが検証で訂正): mise 本体は brew で install、`mise.zsh` で activate 済み。さらに `~/.local/share/mise/installs/` には多数のツール(actionlint/buf/dart/deno/flutter/go 複数版/java/kubectl/dotnet 等)が install 済みだった。**ただしグローバル config に `[tools]` セクションが無いため、どのバージョンもグローバルで有効化されておらず** (`mise current` が空)、PATH では野良 brew が使われていた。`~/.config/mise/config.toml` は settings のみ(`ignored_config_paths`, `experimental`)で tools ゼロ。`everything-cc/.tool-versions` は外部リポ affaan-m/everything-claude-code のクローンで無関係。

2. **二重管理事故が既発生**: Nix `home.packages` に uv があるのに `PATH` で `/usr/local/bin/uv`(Intel brew) が優先されている。

3. **言語ランタイムが野良に散在し再現性ゼロ**:
   - node v25 = brew
   - go 1.25 = amd64/Rosetta
   - python 3.14 = brew (`.tool-versions` の 3.12 と乖離)
   - rust = rustup
   - uv = Intel brew

## Phase 2.5 セカンドオピニオン

**Codex**: `launch-worker.sh:134` の `codex exec ... -q` が現行 codex CLI で非対応(`-q` エラー)のため起動失敗。今回は fallback。**要修正(harness バグ)**。

**Gemini(Google Search grounding)**:
- Nix/mise の境界設計(Nix=土台/mise=ランタイム)を裏付け
- Nix で言語ランタイムを持つ辛さ(flake.lock 肥大化/未キャッシュ版の数十分ビルド/.nvmrc 非互換)は実在を確認
- 二重管理回避策 = 「Nix に言語ランタイムを一切入れない」徹底(mise activate が PATH 末尾で優先)
- devbox/flox は厳密再現性型だが個人 dotfiles で爆速シェル維持なら Nix+mise が最適、乗り換え不要
- `home-manager` の `programs.mise.enable+globalConfig` も選択肢として実在

**bias mitigation**: Claude(自己実ファイル分析) + Gemini の2ファミリ確保。

## Integration Decisions

| 項目 | 判定 | 理由 |
|------|------|------|
| mise 言語ランタイム集約 | **採用** | 唯一の実質 Gap、二重管理事故解消、ユーザー選択 |
| carapace | 不採用 | 小物、優先度低 |
| espanso | 不採用 | cask 宣言のみで YAGNI |
| Nixvim化 | 不採用 | 大作業、利得小 |
| core/dotfiles 2層分離 | 不採用 | 個人1リポで YAGNI |

## Phase 4 実装状況

### 実装済(flake check 通過)

- **`.config/mise/config.toml` 新規作成**: `[tools]` に node=lts, go=1.25, python=3.13, uv=latest (rust は rustup 維持で除外)。Nix と mise の役割分担・二重管理回避ルールをコメントで明記。
- **`nix/home/default.nix` 変更**: `home.packages` から uv 削除(mise 移管)、`home.file` single-file に `.config/mise/config.toml` の outLink 追加。
- **方針**: mise 本体は brew 維持(bootstrap/ハング回避)、`programs.mise` モジュールは使わず config だけ outLink。既存 `.config/zsh/tools/mise.zsh` の activate はそのまま。

### 実装結果(2026-06-03 検証済み)

mise グローバル有効化は **手動 symlink + `mise install` で完了・検証済み**。対話 zsh で全ランタイムが mise installs を PATH 優先で解決:

| ツール | mise current | 改善 |
|---|---|---|
| node | 24.13.0 (lts) | 野良 brew v25 → LTS |
| go | 1.25.4 | **amd64/Rosetta → darwin/arm64 ネイティブ** |
| python | 3.13.6 | brew 3.14 / 旧 3.12 → 3.13 |
| uv | 0.9.7 (aarch64) | Intel brew 0.5.21 → arm64 |

- `~/.config/mise/config.toml` を `~/dotfiles/.config/mise/config.toml` への symlink 化(`mise trust` 済)。既存実ファイル(settings のみ)は `config.toml.pre-nix.bak` に退避しマージ。

### 未実装(残タスク)

- **`nix:switch` は未適用**: uv 削除 + mise outLink の nix 変更はファイルに残存。switch は **`.cursor/hooks.json` / `.codex/config.toml` の clobber**(cmux/Codex の自己書き換えで実ファイル化、本変更とは無関係の既存 drift)でブロック。手動 symlink で mise は有効なため実害なし。clobber 解決後の switch で nix 側も反映。
  - clobber 対処の方向: (a) これらを `home.file` から外す(cmux 同様に管理外) / (b) `backupFileExtension` 設定
- **harness バグ**: `scripts/runtime/launch-worker.sh:134` の `codex exec ... -q` が現行 codex CLI で `-q` 非対応 → Codex Worker 失敗。要 `-q` 削除。
- 野良 brew(node/python/go/uv)の掃除は動作確認後に別途(破壊的)
- (任意) doctor に「ランタイムが mise 由来か」検証追加

## 教訓

- 「この記事のようにしたい」という要望でも、現状把握で大半が Already と判明することがある(Thoroughness over Helpfulness)。正直に「既に実装済み」と伝えるのが誠実。
- 真の Gap は思想ではなく運用(mise が入っているのに使われていない)。実ランタイム解決経路(`which`)を確認して初めて二重管理事故と野良 brew が露出した。
