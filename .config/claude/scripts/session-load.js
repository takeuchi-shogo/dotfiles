#!/usr/bin/env node
// Session state loader — restores previous session context on SessionStart
// Triggered by: hooks.SessionStart
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const STATE_FILE = path.join(process.env.HOME, '.claude', 'session-state', 'last-session.json');

function loadState() {
  try {
    const state = JSON.parse(fs.readFileSync(STATE_FILE, 'utf8'));
    const age = Date.now() - new Date(state.timestamp).getTime();
    const hoursAgo = Math.round(age / (1000 * 60 * 60) * 10) / 10;

    // Only show if session is less than 24 hours old
    if (hoursAgo > 24) return;

    const lines = ['[Session] Previous session state:'];
    lines.push(`  Time: ${hoursAgo}h ago (${state.timestamp})`);
    if (state.cwd) lines.push(`  Dir: ${state.cwd}`);
    if (state.branch) lines.push(`  Branch: ${state.branch}`);
    if (state.modifiedFiles) lines.push(`  Modified: ${state.modifiedFiles.split('\n').filter(Boolean).join(', ')}`);
    if (state.stagedFiles) lines.push(`  Staged: ${state.stagedFiles.split('\n').filter(Boolean).join(', ')}`);
    if (state.recentCommits) {
      lines.push('  Recent commits:');
      state.recentCommits.split('\n').slice(0, 3).forEach((c) => lines.push(`    ${c}`));
    }

    process.stderr.write(lines.join('\n') + '\n');
  } catch {
    // Silently ignore corrupt state files
  }
}

function detectTools() {
  const tools = {
    'Package managers': ['bun', 'pnpm', 'npm', 'yarn'],
    'Languages/Runtimes': ['go', 'node', 'python3', 'ruby', 'rust'],
    'Dev tools': ['gh', 'docker', 'kubectl', 'terraform'],
    'AI tools': ['codex'],
  };

  try {
    const found = [];
    for (const names of Object.values(tools)) {
      for (const name of names) {
        try {
          execSync(`which ${name}`, { timeout: 2000, stdio: 'pipe' });
          found.push(name);
        } catch {
          // Tool not found — skip
        }
      }
    }
    if (found.length > 0) {
      process.stderr.write(`[Session] Available tools: ${found.join(', ')}\n`);
    }
  } catch {
    // Non-blocking — ignore any unexpected errors
  }
}

// Read stdin and pass through
let data = '';
process.stdin.on('data', (chunk) => { data += chunk; });
process.stdin.on('end', () => {
  loadState();
  detectTools();
  process.stdout.write(data);
});
