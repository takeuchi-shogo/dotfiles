{ ... }:

{
  # Phase C1a (2026-04-28): private 固有 module の placeholder。
  # 属性追加は C1b 以降で扱う。base (default.nix) からの module merge により
  # AppleShowAllExtensions = true 等の共通属性は自動継承される。
  # 詳細: docs/plans/active/2026-04-28-nix-migration-phase-c1a-plan.md

  # RunCat Neo は Mac App Store 配信専用 (cask なし、macOS 26+)。
  # mas 経由でインストール。App Store 事前サインインが必要 (mas 自体は
  # nix-darwin homebrew module が pkgs.mas から自動供給、brews への追加不要)。
  homebrew.masApps = {
    "RunCat Neo" = 6757801838;
  };
}
