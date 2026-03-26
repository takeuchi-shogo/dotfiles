#!/usr/bin/env node
// Session state persistence — saves workspace state on Stop/SessionEnd
// Triggered by: hooks.Stop or hooks.SessionEnd
const fs = require("fs");
const path = require("path");
const { execSync } = require("child_process");

const STATE_DIR =
	process.env.CLAUDE_SESSION_STATE_DIR ||
	path.join(process.env.HOME, ".claude", "session-state");
const STATE_FILE = path.join(STATE_DIR, "last-session.json");

function run(cmd) {
	try {
		return execSync(cmd, { encoding: "utf8", timeout: 5000 }).trim();
	} catch {
		return "";
	}
}

function saveState() {
	fs.mkdirSync(STATE_DIR, { recursive: true });

	const state = {
		timestamp: new Date().toISOString(),
		cwd: process.cwd(),
		branch: run("git --no-optional-locks branch --show-current"),
		status: run("git --no-optional-locks status --porcelain"),
		recentCommits: run("git --no-optional-locks log --oneline -5"),
		modifiedFiles: run("git --no-optional-locks diff --name-only"),
		stagedFiles: run("git --no-optional-locks diff --cached --name-only"),
	};

	fs.writeFileSync(STATE_FILE, JSON.stringify(state, null, 2));
	process.stderr.write("[Session] State saved.\n");
}

/**
 * セッション正常終了時に HANDOFF.md を削除する。
 * 次のセッションで古い引き継ぎ情報が残らないようにする。
 */
function cleanupHandoff() {
	const cwd = process.cwd();
	const home = process.env.HOME;
	const candidates = [
		path.join(cwd, "HANDOFF.md"),
		path.join(cwd, "tmp", "HANDOFF.md"),
		path.join(home, "dotfiles", "tmp", "HANDOFF.md"),
	];

	for (const filePath of candidates) {
		try {
			if (fs.existsSync(filePath)) {
				fs.unlinkSync(filePath);
				process.stderr.write(`[Session] HANDOFF.md を削除: ${filePath}\n`);
			}
		} catch {
			// 削除失敗は無視（権限エラー等）
		}
	}
}

// Read stdin (required by hook protocol) and pass through
let data = "";
process.stdin.on("data", (chunk) => {
	data += chunk;
});
process.stdin.on("end", () => {
	try {
		saveState();
		cleanupHandoff();
	} catch (e) {
		process.stderr.write(`[Session] Save failed: ${e.message}\n`);
	}
	process.stdout.write(data);
});
