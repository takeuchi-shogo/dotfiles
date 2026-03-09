#!/usr/bin/env node

/**
 * PreCompact hook: コンテキスト圧縮前に作業状態を stdout に出力する。
 * Claude が圧縮時にこの情報を参照し、重要な状態を保持できる。
 */

const { execSync } = require("child_process");

function run(cmd) {
  try {
    return execSync(cmd, { encoding: "utf-8", timeout: 5000 }).trim();
  } catch {
    return "";
  }
}

const branch = run("git branch --show-current");
const diffStat = run("git diff --stat HEAD");
const stagedStat = run("git diff --cached --stat");
const untrackedFiles = run("git ls-files --others --exclude-standard");

const state = {
  timestamp: new Date().toISOString(),
  git: {
    branch: branch || "(detached)",
    uncommitted_changes: diffStat || "(none)",
    staged_changes: stagedStat || "(none)",
    untracked_files: untrackedFiles
      ? untrackedFiles.split("\n").slice(0, 20)
      : [],
  },
};

// Force checkpoint before compaction
try {
  execSync(
    'python3 $HOME/.claude/scripts/checkpoint_manager.py <<< "{}"',
    { encoding: "utf-8", timeout: 10000, stdio: ["pipe", "pipe", "pipe"] },
  );
} catch {
  // Non-critical — checkpoint failure shouldn't block compaction
}

console.log(JSON.stringify(state, null, 2));
