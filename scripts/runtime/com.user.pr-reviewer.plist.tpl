<?xml version="1.0" encoding="UTF-8"?>
<!--
  PR Reviewer launchd agent template.

  Install:
    sed "s|@@HOME@@|$HOME|g" com.user.pr-reviewer.plist.tpl \
      > ~/Library/LaunchAgents/com.user.pr-reviewer.plist
    launchctl bootstrap "gui/$UID" ~/Library/LaunchAgents/com.user.pr-reviewer.plist

  Refs: docs/playbooks/pr-reviewer-launchd.md
-->
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.pr-reviewer</string>

    <key>ProgramArguments</key>
    <array>
        <string>@@HOME@@/dotfiles/scripts/runtime/poll-pr-reviewer.sh</string>
    </array>

    <!-- 10 分間隔 (GitHub Search API レート枠保護) -->
    <key>StartInterval</key>
    <integer>600</integer>

    <!-- launchd load 直後の即時実行は避ける (host gate 評価のみで早期 exit させたい) -->
    <key>RunAtLoad</key>
    <false/>

    <!-- 二重起動防止 -->
    <key>AbandonProcessGroup</key>
    <false/>

    <!-- launchd 自身の stdout/stderr。スクリプト内ログは ~/Library/Logs/pr-reviewer/poll.log -->
    <key>StandardOutPath</key>
    <string>@@HOME@@/Library/Logs/pr-reviewer/launchd.out.log</string>
    <key>StandardErrorPath</key>
    <string>@@HOME@@/Library/Logs/pr-reviewer/launchd.err.log</string>

    <!-- PATH: gh / cmux / jq の解決に必要 (Homebrew + system) -->
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string>
        <key>HOME</key>
        <string>@@HOME@@</string>
    </dict>
</dict>
</plist>
