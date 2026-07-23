cask "agentpeek" do
  version "0.2.59"
  sha256 "f8500a08fbdfc4066f5832d2d4c0c93dee97fd647abe8d8a1131cad18d4bab1e"

  url "https://dl.agentpeek.app/AgentPeek-#{version}.dmg"
  name "AgentPeek"
  desc "Manage coding agents from the Mac notch"
  homepage "https://agentpeek.app/"

  livecheck do
    url "https://dl.agentpeek.app/appcast.xml"
    strategy :sparkle
  end

  auto_updates true
  depends_on macos: :sonoma
  depends_on arch: :arm64

  app "AgentPeek.app"

  uninstall quit: "app.agentpeek.desktop"

  zap trash: [
    "~/Library/Caches/app.agentpeek.desktop",
    "~/Library/Preferences/app.agentpeek.desktop.plist",
    "~/Library/Application Support/AgentPeek",
  ]
end
