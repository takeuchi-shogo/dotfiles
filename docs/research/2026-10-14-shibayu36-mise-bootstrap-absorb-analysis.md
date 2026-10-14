---
source: "https://blog.shibayu36.org/entry/2026/10/13/173000"
date: 2026-10-14
status: analyzed
topic-family: "nix-mise-dotfiles-environment (N=2, prior=2026-06-02-typhoon-nix-mise)"
---

## Source

- **URL**: https://blog.shibayu36.org/entry/2026/10/13/173000
- **タイトル**: 私物Macと仕事Macのdotfilesとアプリ管理をmise bootstrapで管理しやすくした
- **著者**: 柴崎優季 (@shibayu36), 2026-10-13
- **関連投稿**: https://x.com/shibayu36/status/2109968222690623902
  （本文:「mise bootstrapめっちゃ便利だった」+ 上記記事へのリンク。追加の技術詳細なし）
- **参照リポジトリ差分**（記事内）: https://github.com/shibayu36/config-file/compare/5352a37...aba67d4

## 記事の主張

これまでパッケージ群（Brewfile）・dotfiles 群（`ln -s` スクリプト）・Mac 設定群（`defaults write` スクリプト）が別ファイルに分かれ、冪等でもなく、私物/仕事の層分けもなかった。

`mise bootstrap`（2026年6月入機能）を使うと、次を **1 つの `config.toml` に宣言**し、`mise bootstrap` 1 コマンドで差分適用できる。

- パッケージ（`[bootstrap.packages]` — brew / brew-cask / mas）
- dotfiles（`[dotfiles]` — デフォルトは symlink）
- macOS defaults（`[bootstrap.macos.defaults.*]`）

私物/仕事の切り替えは `~/.config/mise/miserc.local.toml` の `env` で、共通 `config.toml` に加えて `config.personal.toml` / `config.work.toml` を重ねる。マシンごとの中身の微差にも対応できる、と記事は述べる。ランタイム管理で既に mise を使っていたため道具が増えない点も採用理由。chezmoi や Nix も調査したが、symlink 運用を変えずに済むシンプルさで bootstrap を選んだ、とある。

## Gap Analysis (Pass 1: 存在チェック)

| 手法 | 判定 | 詳細 |
|------|------|------|
| パッケージ・dotfiles・macOS 設定の宣言的一括適用 | Already | Nix home-manager が設定配布・CLI/設定の土台を担う（`nix/home/default.nix`、`nix/README.md`: symlink.sh 廃止・home-manager 移行済み）。役割分担コメントは `.config/mise/config.toml` にも明記 |
| personal / work（私物/仕事）の層分け | Already | `nix/flake.nix` の `darwinConfigurations.{private,work}` + `nix/darwin/{private,work}.nix`。反映は `task nix:switch PROFILE=private\|work`（`nix/README.md`） |
| mise をランタイム管理に使う | Already | typhoon absorb（2026-06-02）でグローバル `[tools]` 集約済み。本記事の bootstrap は「配布・層分け」側の話で、ランタイム版固定とは別軸 |
| Brewfile / symlink スクリプト / defaults スクリプトを mise bootstrap の1ファイルに寄せる移行 | N/A（移行しない） | 既に Nix 側が同等以上の責務を持つ。二重の宣言ソースを増やすだけになる |
| chezmoi への乗り換え | N/A | 記事も調査のみ。dotfiles は Nix 配備済み |

## Integration Decisions

| 項目 | 判定 | 理由 |
|------|------|------|
| mise bootstrap への移行（packages / dotfiles / macos.defaults を config.toml に寄せる） | **不採用** | Nix home-manager が配布を、`private`/`work` ホスト分離が層分けを既に担っている。記事の課題（3スクリプト分散・冪等性・私物/仕事の分離）は現状で解消済み |
| personal/work 用 `config.*.toml` + `miserc.local.toml` env 切替の模倣 | **不採用** | 同上。既存は flake のホスト module で切替 |
| mise のランタイム役割の維持 | **継続** | typhoon absorb の方針どおり。bootstrap 機能の採用とは独立 |

## Phase 4 実装状況

実装なし（分析記録のみ）。設定ファイル・Task・symlink の変更は行わない。

## 教訓

- 同 family（nix-mise-dotfiles-environment）でも、記事が解く問題が「ランタイム版固定」か「配布・ホスト層分け」かで Already の根拠が違う。typhoon は前者の Gap を埋め、本記事は後者で Already。
- 「mise を既に使っているから bootstrap も足す」は道具の統一には見えるが、Nix と宣言が二重になる。Thoroughness over Helpfulness: 便利さの証言（X 投稿含む）だけでは移行根拠にしない。
