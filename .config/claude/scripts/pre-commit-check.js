#!/usr/bin/env node
// Pre-commit quality gate — checks for common issues before commit
// Triggered by: hooks.PreToolUse (Bash matching git commit)
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

function run(cmd) {
  try {
    return execSync(cmd, { encoding: 'utf8', timeout: 10000 }).trim();
  } catch {
    return '';
  }
}

function checkStagedFiles() {
  const warnings = [];

  const staged = run('git diff --cached --name-only');
  if (!staged) return warnings;

  const files = staged.split('\n').filter(Boolean);

  // Check for secrets patterns in file names
  const secretPatterns = [
    /\.(env|env\.local|env\.production)$/,
    /credentials\.json$/,
    /\.pem$/,
    /(?:^|[/._-])secrets?(?:\.[a-z]+)?$/i,
  ];

  for (const file of files) {
    for (const pattern of secretPatterns) {
      if (pattern.test(file)) {
        warnings.push(`[WARN] Potentially sensitive file staged: ${file}`);
      }
    }
  }

  // Check staged content — only added lines
  const diff = run('git diff --cached');
  const addedLines = diff.split('\n').filter((l) => l.startsWith('+') && !l.startsWith('+++'));
  const addedContent = addedLines.join('\n');

  // Check for hardcoded secrets in added lines
  const contentPatterns = [
    { regex: /sk-[a-zA-Z0-9]{20,}/, desc: 'API key (sk-...)' },
    { regex: /ghp_[a-zA-Z0-9]{36,}/, desc: 'GitHub token' },
    { regex: /AKIA[A-Z0-9]{16}/, desc: 'AWS access key' },
    { regex: /password\s*[:=]\s*['"][^'"]{8,}['"]/, desc: 'Hardcoded password' },
  ];

  for (const { regex, desc } of contentPatterns) {
    if (regex.test(addedContent)) {
      warnings.push(`[CRITICAL] Possible ${desc} detected in staged changes`);
    }
  }

  // Check for debug artifacts in added lines
  const debugPatterns = [
    { regex: /console\.log\(/, desc: 'console.log' },
    { regex: /debugger;/, desc: 'debugger statement' },
    { regex: /TODO.*HACK|FIXME.*HACK/, desc: 'HACK comment' },
  ];
  for (const { regex, desc } of debugPatterns) {
    const matches = addedLines.filter((l) => regex.test(l));
    if (matches.length > 0) {
      warnings.push(`[INFO] ${desc} found in ${matches.length} added line(s)`);
    }
  }

  return warnings;
}

// Read stdin (hook protocol JSON) and pass through
// Note: matcher is set to "Bash(git commit *)" so this only fires on commits
let data = '';
process.stdin.on('data', (chunk) => { data += chunk; });
process.stdin.on('end', () => {
  try {
    const warnings = checkStagedFiles();
    if (warnings.length > 0) {
      process.stderr.write('[Pre-commit] Quality check results:\n');
      warnings.forEach((w) => process.stderr.write(`  ${w}\n`));
      const hasCritical = warnings.some((w) => w.startsWith('[CRITICAL]'));
      if (hasCritical) {
        const reasons = warnings.filter((w) => w.startsWith('[CRITICAL]')).join('; ');
        process.stderr.write(`[Pre-commit] BLOCKED: ${reasons}\n`);
        process.stdout.write(JSON.stringify({
          decision: 'block',
          reason: `セキュリティ上の問題が検出されました: ${reasons}`,
        }), () => process.exit(2));
      }
    }
  } catch {
    // Non-blocking — don't prevent commit on check failure
  }
  process.stdout.write(data);
});
