{ ... }:

{
  # Phase C1a (2026-04-28): work 固有 module の placeholder。
  # 新品 work Mac での実機検証が未実施のため空 module から開始。
  # base (default.nix) からの module merge で AppleShowAllExtensions 等の
  # 共通属性は自動継承される (Codex Plan Gate HIGH-2 の検証で実証済)。
  # 詳細: docs/plans/active/2026-04-28-nix-migration-phase-c1a-plan.md

  # RunCat Neo は Mac App Store 配信専用 (cask なし、macOS 26+)。
  # mas 経由でインストール。App Store 事前サインインが必要 (mas 自体は
  # nix-darwin homebrew module が pkgs.mas から自動供給、brews への追加不要)。
  homebrew.masApps = {
    "RunCat Neo" = 6757801838;
  };
}
