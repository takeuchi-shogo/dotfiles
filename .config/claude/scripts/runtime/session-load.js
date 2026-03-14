#!/usr/bin/env node
// Session state loader — restores previous session context on SessionStart
// Triggered by: hooks.SessionStart
const fs = require("fs");
const path = require("path");
const { execSync } = require("child_process");

const STATE_FILE = path.join(
	process.env.HOME,
	".claude",
	"session-state",
	"last-session.json",
);

function loadState() {
	try {
		const state = JSON.parse(fs.readFileSync(STATE_FILE, "utf8"));
		const age = Date.now() - new Date(state.timestamp).getTime();
		const hoursAgo = Math.round((age / (1000 * 60 * 60)) * 10) / 10;

		// Only show if session is less than 24 hours old
		if (hoursAgo > 24) return;

		const lines = ["[Session] Previous session state:"];
		lines.push(`  Time: ${hoursAgo}h ago (${state.timestamp})`);
		if (state.cwd) lines.push(`  Dir: ${state.cwd}`);
		if (state.branch) lines.push(`  Branch: ${state.branch}`);
		if (state.modifiedFiles)
			lines.push(
				`  Modified: ${state.modifiedFiles.split("\n").filter(Boolean).join(", ")}`,
			);
		if (state.stagedFiles)
			lines.push(
				`  Staged: ${state.stagedFiles.split("\n").filter(Boolean).join(", ")}`,
			);
		if (state.recentCommits) {
			lines.push("  Recent commits:");
			state.recentCommits
				.split("\n")
				.slice(0, 3)
				.forEach((c) => lines.push(`    ${c}`));
		}

		process.stderr.write(lines.join("\n") + "\n");
	} catch {
		// Silently ignore corrupt state files
	}
}

function detectTools() {
	const tools = {
		"Package managers": ["pnpm", "npm", "yarn"],
		"Languages/Runtimes": ["go", "node", "python3", "ruby", "rust"],
		"Dev tools": ["gh", "docker", "kubectl", "terraform"],
		"AI tools": ["codex", "gemini"],
	};

	try {
		const found = [];
		for (const names of Object.values(tools)) {
			for (const name of names) {
				try {
					execSync(`which ${name}`, { timeout: 2000, stdio: "pipe" });
					found.push(name);
				} catch {
					// Tool not found — skip
				}
			}
		}
		if (found.length > 0) {
			process.stderr.write(`[Session] Available tools: ${found.join(", ")}\n`);
		}
	} catch {
		// Non-blocking — ignore any unexpected errors
	}
}

function loadLearningsForProfile(profile) {
	const dataDir =
		process.env.AUTOEVOLVE_DATA_DIR ||
		path.join(process.env.HOME, ".claude", "agent-memory");
	const learningsDir = path.join(dataDir, "learnings");

	if (!fs.existsSync(learningsDir)) return;

	const allEntries = [];
	for (const file of fs.readdirSync(learningsDir)) {
		if (!file.endsWith(".jsonl")) continue;
		try {
			const lines = fs
				.readFileSync(path.join(learningsDir, file), "utf8")
				.split("\n");
			for (const line of lines) {
				if (!line.trim()) continue;
				try {
					allEntries.push(JSON.parse(line));
				} catch {
					/* skip corrupt lines */
				}
			}
		} catch {
			/* skip unreadable files */
		}
	}

	if (allEntries.length === 0) return;

	let filtered;
	const now = Date.now();
	const oneDayMs = 86400000;

	switch (profile) {
		case "planning":
			filtered = allEntries
				.filter((e) => ["decision", "pattern"].includes(e.type || e.category))
				.filter((e) => (e.importance ?? 0.5) >= 0.4)
				.sort((a, b) => (b.importance ?? 0.5) - (a.importance ?? 0.5))
				.slice(0, 8);
			break;

		case "debugging":
			filtered = allEntries
				.filter((e) => ["error", "correction"].includes(e.type || e.category))
				.filter((e) => (e.importance ?? 0.5) >= 0.3)
				.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
				.slice(0, 10);
			break;

		case "incident":
			filtered = allEntries
				.filter((e) => new Date(e.timestamp).getTime() > now - oneDayMs)
				.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
			break;

		case "task-aware": {
			// arXiv:2603.10600 Adaptive Memory Retrieval — keyword-based approximation
			// git diff/status からキーワードを抽出し、learnings を関連度でフィルタ
			let keywords = [];
			try {
				const diffOutput = execSync(
					"git diff --name-only HEAD 2>/dev/null || true",
					{ timeout: 3000, encoding: "utf8" },
				).trim();
				const statusOutput = execSync(
					"git status --porcelain 2>/dev/null || true",
					{ timeout: 3000, encoding: "utf8" },
				).trim();
				const files = [...diffOutput.split("\n"), ...statusOutput.split("\n")]
					.map((l) => l.trim().replace(/^[MADRCU?! ]+\s*/, ""))
					.filter(Boolean);
				for (const f of files) {
					const parts = f.replace(/\.[^.]+$/, "").split(/[/\\-_]/);
					keywords.push(...parts.filter((p) => p.length > 2));
				}
			} catch {
				/* ignore git errors */
			}

			if (keywords.length === 0) {
				filtered = allEntries
					.filter((e) => (e.importance ?? 0.5) >= 0.4)
					.sort((a, b) => (b.importance ?? 0.5) - (a.importance ?? 0.5))
					.slice(0, 5);
			} else {
				const kwSet = new Set(keywords.map((k) => k.toLowerCase()));
				filtered = allEntries
					.map((e) => {
						const text = JSON.stringify(e).toLowerCase();
						const matchCount = [...kwSet].filter((kw) =>
							text.includes(kw),
						).length;
						return { entry: e, matchCount };
					})
					.filter((x) => x.matchCount > 0)
					.sort(
						(a, b) =>
							b.matchCount - a.matchCount ||
							(b.entry.importance ?? 0.5) - (a.entry.importance ?? 0.5),
					)
					.slice(0, 8)
					.map((x) => x.entry);
			}
			break;
		}

		default:
			filtered = allEntries
				.filter((e) => (e.importance ?? 0.5) >= 0.4)
				.sort((a, b) => (b.importance ?? 0.5) - (a.importance ?? 0.5))
				.slice(0, 5);
			break;
	}

	if (filtered.length === 0) return;

	const lines = [
		`[Learnings: ${profile}] 関連する過去の学び (${filtered.length}件):`,
	];
	for (const e of filtered) {
		const msg =
			e.error_pattern || e.message || e.rule || e.detail || e.name || "";
		const recovery = e.recovery_action
			? ` -> ${String(e.recovery_action).slice(0, 80)}`
			: "";
		const imp = e.importance != null ? ` [i=${e.importance}]` : "";
		lines.push(
			`  - ${e.type || e.category || "?"}${imp}: ${String(msg).slice(0, 120)}${recovery}`,
		);
	}

	process.stderr.write(lines.join("\n") + "\n");
}

// Read stdin and pass through
let data = "";
process.stdin.on("data", (chunk) => {
	data += chunk;
});
process.stdin.on("end", () => {
	loadState();

	// Load profile from last checkpoint or task-aware
	let profile = "task-aware";
	try {
		const cpPath = path.join(
			process.env.HOME,
			".claude",
			"session-state",
			"last-checkpoint.json",
		);
		if (fs.existsSync(cpPath)) {
			const cp = JSON.parse(fs.readFileSync(cpPath, "utf8"));
			profile = cp.active_profile || "default";
		}
	} catch {
		/* ignore */
	}

	loadLearningsForProfile(profile);
	process.stdout.write(data);
});
