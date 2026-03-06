#!/usr/bin/env node
// Auto-format files after Edit/Write — runs Prettier or gofmt based on extension
// Triggered by: hooks.PostToolUse (Edit|Write)
const { execSync } = require('child_process');

function which(cmd) {
  try {
    execSync(`which ${cmd}`, { stdio: 'pipe', timeout: 3000 });
    return true;
  } catch {
    return false;
  }
}

function format(filePath) {
  if (!filePath) return;

  const prettierExts = /\.(tsx?|jsx?|json|css|scss|html|md|yaml|yml)$/;
  const goExts = /\.go$/;

  try {
    if (prettierExts.test(filePath) && which('npx')) {
      execSync(`npx prettier --write "${filePath}"`, { stdio: 'pipe', timeout: 15000 });
      process.stderr.write(`[Format] prettier: ${filePath}\n`);
    } else if (goExts.test(filePath) && which('gofmt')) {
      execSync(`gofmt -w "${filePath}"`, { stdio: 'pipe', timeout: 10000 });
      process.stderr.write(`[Format] gofmt: ${filePath}\n`);
    }
  } catch {
    // Non-blocking — don't fail the tool use
  }
}

let data = '';
process.stdin.on('data', (chunk) => { data += chunk; });
process.stdin.on('end', () => {
  try {
    const payload = JSON.parse(data);
    const filePath = payload?.tool_input?.file_path;
    format(filePath);
  } catch {
    // Ignore parse errors
  }
  process.stdout.write(data);
});
