#!/usr/bin/env node
// Token-aware compaction reminder — suggests compaction after many edits
// Triggered by: hooks.PostToolUse (Edit|Write)
const fs = require("fs");
const path = require("path");

const COUNTER_FILE = path.join(
  process.env.HOME,
  ".claude",
  "session-state",
  "edit-counter.json",
);
const LOOP_WINDOW_MS = 10 * 60 * 1000; // 10 minutes
const LOOP_THRESHOLD = 3;
const MAX_RECENT_EDITS = 20;

function getCounter() {
  try {
    return JSON.parse(fs.readFileSync(COUNTER_FILE, "utf8"));
  } catch {
    return { count: 0, lastReset: Date.now(), recentEdits: [] };
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

// Extract edited file path from hook JSON input
function extractFilePath(jsonStr) {
  try {
    const input = JSON.parse(jsonStr);
    // Edit tool: input.tool_input.file_path
    // Write tool: input.tool_input.file_path
    if (input.tool_input && input.tool_input.file_path) {
      return input.tool_input.file_path;
    }
  } catch {
    // Not valid JSON — ignore
  }
  return null;
}

// Check for edit loops on the same file
function checkEditLoop(counter, filePath) {
  if (!filePath) return;
  if (!counter.recentEdits) counter.recentEdits = [];

  const now = Date.now();
  counter.recentEdits.push({ file: filePath, timestamp: now });

  // Prune stale entries by time first, then cap by count
  counter.recentEdits = counter.recentEdits
    .filter((e) => now - e.timestamp < LOOP_WINDOW_MS)
    .slice(-MAX_RECENT_EDITS);

  // Count edits to this file within the (already-filtered) window
  const recentCount = counter.recentEdits.filter(
    (e) => e.file === filePath,
  ).length;

  if (recentCount >= LOOP_THRESHOLD) {
    counter._loopDetected = { file: filePath, count: recentCount };
  }
}

// Read stdin and pass through
let data = "";
process.stdin.on("data", (chunk) => {
  data += chunk;
});
process.stdin.on("end", () => {
  const counter = getCounter();

  // Reset counter if more than 2 hours old
  if (Date.now() - counter.lastReset > 2 * 60 * 60 * 1000) {
    counter.count = 0;
    counter.lastReset = Date.now();
    counter.recentEdits = [];
  }

  counter.count++;

  // Check for edit loops
  const filePath = extractFilePath(data);
  checkEditLoop(counter, filePath);

  saveCounter(counter);

  // Suggest compaction at thresholds
  if (counter.count === 30) {
    process.stderr.write(
      "[Token] 30 edits in this session. Consider compacting context if response quality degrades.\n",
    );
  } else if (counter.count === 50) {
    process.stderr.write(
      "[Token] 50 edits reached. Strongly recommend delegating to subagents or compacting.\n",
    );
  }

  // Output loop detection as additionalContext so AI sees it
  if (counter._loopDetected) {
    const loop = counter._loopDetected;
    const basename = path.basename(loop.file);
    try {
      const parsed = JSON.parse(data);
      const output = {
        ...parsed,
        hookSpecificOutput: {
          hookEventName: "PostToolUse",
          additionalContext:
            `[Loop Detection] ${basename} が ${loop.count} 回編集されています（10分以内）。` +
            `修正ループの可能性があります。このファイルへの編集を一旦停止し、アプローチを見直してください。` +
            `この警告は情報提供であり、修正不要です。`,
        },
      };
      process.stdout.write(JSON.stringify(output));
    } catch {
      process.stdout.write(data);
    }
  } else {
    process.stdout.write(data);
  }
});
