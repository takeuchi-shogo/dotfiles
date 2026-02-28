#!/usr/bin/env node
// Session state persistence — saves workspace state on Stop/SessionEnd
// Triggered by: hooks.Stop or hooks.SessionEnd
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const STATE_DIR = path.join(process.env.HOME, '.claude', 'session-state');
const STATE_FILE = path.join(STATE_DIR, 'last-session.json');

function run(cmd) {
  try {
    return execSync(cmd, { encoding: 'utf8', timeout: 5000 }).trim();
  } catch {
    return '';
  }
}

function saveState() {
  fs.mkdirSync(STATE_DIR, { recursive: true });

  const state = {
    timestamp: new Date().toISOString(),
    cwd: process.cwd(),
    branch: run('git branch --show-current'),
    status: run('git status --porcelain'),
    recentCommits: run('git log --oneline -5'),
    modifiedFiles: run('git diff --name-only'),
    stagedFiles: run('git diff --cached --name-only'),
  };

  fs.writeFileSync(STATE_FILE, JSON.stringify(state, null, 2));
  process.stderr.write('[Session] State saved.\n');
}

// Read stdin (required by hook protocol) and pass through
let data = '';
process.stdin.on('data', (chunk) => { data += chunk; });
process.stdin.on('end', () => {
  try {
    saveState();
  } catch (e) {
    process.stderr.write(`[Session] Save failed: ${e.message}\n`);
  }
  process.stdout.write(data);
});
