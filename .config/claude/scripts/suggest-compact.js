#!/usr/bin/env node
// Token-aware compaction reminder — suggests compaction after many edits
// Triggered by: hooks.PostToolUse (Edit|Write)
const fs = require('fs');
const path = require('path');

const COUNTER_FILE = path.join(process.env.HOME, '.claude', 'session-state', 'edit-counter.json');

function getCounter() {
  try {
    return JSON.parse(fs.readFileSync(COUNTER_FILE, 'utf8'));
  } catch {
    return { count: 0, lastReset: Date.now() };
  }
}

function saveCounter(counter) {
  try {
    const dir = path.dirname(COUNTER_FILE);
    fs.mkdirSync(dir, { recursive: true });
    fs.writeFileSync(COUNTER_FILE, JSON.stringify(counter));
  } catch {
    // Non-critical — counter loss is acceptable
  }
}

// Read stdin and pass through
let data = '';
process.stdin.on('data', (chunk) => { data += chunk; });
process.stdin.on('end', () => {
  const counter = getCounter();

  // Reset counter if more than 2 hours old
  if (Date.now() - counter.lastReset > 2 * 60 * 60 * 1000) {
    counter.count = 0;
    counter.lastReset = Date.now();
  }

  counter.count++;
  saveCounter(counter);

  // Suggest compaction at thresholds
  if (counter.count === 30) {
    process.stderr.write('[Token] 30 edits in this session. Consider compacting context if response quality degrades.\n');
  } else if (counter.count === 50) {
    process.stderr.write('[Token] 50 edits reached. Strongly recommend delegating to subagents or compacting.\n');
  }

  process.stdout.write(data);
});
