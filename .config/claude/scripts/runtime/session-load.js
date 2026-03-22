#!/usr/bin/env node
// Session state loader — restores previous session context on SessionStart
// Triggered by: hooks.SessionStart
const fs = require("fs");
const path = require("path");
const { execSync } = require("child_process");

const STATE_FILE = path.join(
	require("os").homedir(),
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

/**
 * HANDOFF.md を検索して読み込む。
 * 24時間以内のものがあれば stderr に出力し true を返す。
 * @returns {boolean} HANDOFF.md が有効だった場合 true
 */
function loadHandoff() {
	const cwd = process.cwd();
	const home = require("os").homedir();
	// 検索パス: cwd直下 → cwd/tmp/ → ~/dotfiles/tmp/
	const candidates = [
		path.join(cwd, "HANDOFF.md"),
		path.join(cwd, "tmp", "HANDOFF.md"),
		path.join(home, "dotfiles", "tmp", "HANDOFF.md"),
	];

	for (const filePath of candidates) {
		try {
			if (!fs.existsSync(filePath)) continue;
			const stat = fs.statSync(filePath);
			const ageMs = Date.now() - stat.mtimeMs;
			const ageHours = ageMs / (1000 * 60 * 60);

			if (ageHours > 24) {
				process.stderr.write(
					`[Handoff] ${filePath} は ${Math.round(ageHours)}時間前のものです（24時間超過 — スキップ）\n`,
				);
				continue;
			}

			const content = fs.readFileSync(filePath, "utf8").trim();
			if (!content) continue;

			const lines = [
				`[Handoff] 前セッションからの引き継ぎ (${Math.round(ageHours * 10) / 10}時間前, ${filePath}):`,
				content,
			];
			process.stderr.write(lines.join("\n") + "\n");
			return true;
		} catch {
			// ファイル読み込みエラーは無視
		}
	}
	return false;
}

/**
 * PreCompact 時に設定された handoff-requested フラグを検出し、
 * HANDOFF.md の生成を促すメッセージを表示する。
 * フラグは一度表示したら削除する（ワンショット）。
 */
function checkHandoffRequest() {
	const flagPath = path.join(
		require("os").homedir(),
		".claude",
		"session-state",
		"handoff-requested.json",
	);

	try {
		if (!fs.existsSync(flagPath)) return;

		const data = JSON.parse(fs.readFileSync(flagPath, "utf8"));
		const ageMs = Date.now() - new Date(data.timestamp).getTime();
		const ageHours = ageMs / (1000 * 60 * 60);

		// 24時間超過なら削除してスキップ
		if (ageHours > 24) {
			fs.unlinkSync(flagPath);
			return;
		}

		process.stderr.write(
			`[Handoff] HANDOFF.md の生成が必要です（${data.reason || "pre-compact"}）。` +
				`/checkpoint を実行するか、tmp/HANDOFF.md に作業状態を保存してください。` +
				` (branch: ${data.git_branch || "(unknown)"})\n`,
		);

		// ワンショット: 一度表示したら削除
		fs.unlinkSync(flagPath);
	} catch {
		// Non-critical — ignore errors
	}
}

/**
 * Detect project test runner and suggest running tests first (Willison pattern).
 * "First run the tests" establishes a baseline at session start.
 */
function suggestTestBaseline() {
	const cwd = process.cwd();
	const testRunners = [
		{ file: "package.json", cmd: "npm test", check: "scripts" },
		{ file: "Makefile", cmd: "make test", check: "test:" },
		{ file: "Taskfile.yml", cmd: "task test", check: "test:" },
		{ file: "pyproject.toml", cmd: "uv run pytest", check: null },
		{ file: "pytest.ini", cmd: "uv run pytest", check: null },
		{ file: "setup.py", cmd: "python -m pytest", check: null },
		{ file: "go.mod", cmd: "go test ./...", check: null },
		{ file: "Cargo.toml", cmd: "cargo test", check: null },
	];

	for (const runner of testRunners) {
		const filePath = path.join(cwd, runner.file);
		try {
			if (!fs.existsSync(filePath)) continue;
			if (runner.check) {
				const content = fs.readFileSync(filePath, "utf8");
				if (!content.includes(runner.check)) continue;
			}
			process.stderr.write(
				`[Test Baseline] Test runner detected (${runner.file}). ` +
					`Consider running tests first to establish a baseline: \`${runner.cmd}\`\n`,
			);
			return;
		} catch {
			// Skip unreadable files
		}
	}
}

/**
 * Run a fast baseline test check at session start.
 * Reports test status via stderr so the agent knows the current state.
 * Only runs if CLAUDE_BASELINE_CHECK=1 is set (opt-in).
 * Timeout: 30s to avoid blocking session start.
 *
 * Article insight: "The agent would fix the existing breakage before
 * touching anything new. This prevented the compounding problem where
 * an agent starts a new feature on top of a broken foundation."
 */
function runBaselineCheck() {
	if (process.env.CLAUDE_BASELINE_CHECK !== "1") return;

	const cwd = process.cwd();
	const testRunners = [
		{ file: "package.json", cmd: "npm test", check: "scripts" },
		{ file: "Makefile", cmd: "make test", check: "test:" },
		{ file: "Taskfile.yml", cmd: "task test", check: "test:" },
		{ file: "pyproject.toml", cmd: "uv run pytest --tb=line -q", check: null },
		{ file: "go.mod", cmd: "go test ./... -short", check: null },
		{ file: "Cargo.toml", cmd: "cargo test --quiet", check: null },
	];

	let testCmd = null;
	for (const runner of testRunners) {
		const filePath = path.join(cwd, runner.file);
		try {
			if (!fs.existsSync(filePath)) continue;
			if (runner.check) {
				const content = fs.readFileSync(filePath, "utf8");
				if (!content.includes(runner.check)) continue;
			}
			testCmd = runner.cmd;
			break;
		} catch {
			continue;
		}
	}

	if (!testCmd) return;

	try {
		execSync(testCmd, {
			timeout: 30000,
			cwd,
			stdio: ["pipe", "pipe", "pipe"],
			env: { ...process.env, NO_COLOR: "1", CI: "1" },
		});
		process.stderr.write(
			`[Baseline] ✓ テスト通過 (${testCmd}) — 安全に新しい作業を開始できます\n`,
		);
	} catch (err) {
		const output = (err.stdout || "") + (err.stderr || "");
		const lastLines = output.toString().split("\n").slice(-5).join("\n");
		process.stderr.write(
			`[Baseline] ✗ テスト失敗 (${testCmd}) — 新しい作業の前に既存の問題を修正してください\n` +
				`${lastLines}\n`,
		);
		// additionalContext として stdout に出力 — エージェントはこの情報を無視できない
		process.stdout.write(
			`[Baseline FAILED] テストが壊れています。新機能の前にこれを修正してください: \`${testCmd}\`\n`,
		);
	}
}

/**
 * Snapshot active plans at session start.
 * Ralph Loop (completion-gate.py) uses this to only block on plans
 * created or modified during the current session.
 */
function snapshotActivePlans() {
	const planDirs = [
		path.join(process.cwd(), "docs", "plans", "active"),
		path.join(process.cwd(), "tmp", "plans"),
	];
	const snapshot = { timestamp: Date.now(), plans: {} };

	for (const dir of planDirs) {
		try {
			if (!fs.existsSync(dir)) continue;
			for (const file of fs.readdirSync(dir)) {
				if (!file.endsWith(".md")) continue;
				const filePath = path.join(dir, file);
				const stat = fs.statSync(filePath);
				snapshot.plans[file] = { mtime: stat.mtimeMs };
			}
		} catch {
			// Directory unreadable — skip
		}
	}

	try {
		const stateDir = path.join(
			require("os").homedir(),
			".claude",
			"session-state",
		);
		if (!fs.existsSync(stateDir)) fs.mkdirSync(stateDir, { recursive: true });
		fs.writeFileSync(
			path.join(stateDir, "active-plans-snapshot.json"),
			JSON.stringify(snapshot),
		);
	} catch {
		// Non-critical
	}
}

/**
 * Load feature_list.json and display next incomplete feature.
 * Also snapshots feature passes state for session-focus detection.
 */
function loadFeatureList() {
	const cwd = process.cwd();
	const featurePath = path.join(cwd, "feature_list.json");

	if (!fs.existsSync(featurePath)) return;

	try {
		const data = JSON.parse(fs.readFileSync(featurePath, "utf8"));
		const features = data.features || [];
		const done = features.filter((f) => f.passes).length;
		const total = features.length;
		const next = features.find((f) => !f.passes);

		const lines = [`[Feature Tracker] ${done}/${total} features completed`];
		if (next) {
			lines.push(`  Next: ${next.id} - ${next.description}`);
			if (next.steps && next.steps.length > 0) {
				lines.push(
					`  Steps: ${next.steps.slice(0, 3).join(", ")}${next.steps.length > 3 ? " ..." : ""}`,
				);
			}
		} else {
			lines.push("  All features completed!");
		}
		process.stderr.write(lines.join("\n") + "\n");

		// Snapshot passes state for session-focus detection
		const stateDir = path.join(
			require("os").homedir(),
			".claude",
			"session-state",
		);
		if (!fs.existsSync(stateDir)) {
			fs.mkdirSync(stateDir, { recursive: true });
		}
		const passesSnapshot = {};
		for (const f of features) {
			passesSnapshot[f.id] = f.passes || false;
		}
		fs.writeFileSync(
			path.join(stateDir, "feature-passes-snapshot.json"),
			JSON.stringify({
				timestamp: Date.now(),
				passes: passesSnapshot,
			}),
		);
	} catch (err) {
		process.stderr.write(`[Feature Tracker] Failed to load: ${err.message}\n`);
	}
}

/**
 * Load progress.log and display recent entries.
 */
function loadProgressLog() {
	const cwd = process.cwd();
	const logPath = path.join(cwd, "progress.log");

	if (!fs.existsSync(logPath)) return;

	try {
		const content = fs.readFileSync(logPath, "utf8").trim();
		if (!content) return;

		const allLines = content.split("\n");
		const recent = allLines.slice(-3);
		const lines = [`[Progress Log] Recent entries (${allLines.length} total):`];
		for (const entry of recent) {
			lines.push(`  ${entry}`);
		}
		process.stderr.write(lines.join("\n") + "\n");
	} catch (err) {
		process.stderr.write(`[Progress Log] Failed to load: ${err.message}\n`);
	}
}

/**
 * Suggest a refactor session if recent progress.log entries
 * are all feature-addition work.
 */
function suggestRefactorSession() {
	const cwd = process.cwd();
	const logPath = path.join(cwd, "progress.log");

	if (!fs.existsSync(logPath)) return;

	try {
		const content = fs.readFileSync(logPath, "utf8").trim();
		if (!content) return;

		const lines = content.split("\n");
		const recent = lines.slice(-5);
		if (recent.length < 5) return;

		const featKeywords = ["feat", "add", "implement", "new"];
		const allFeats = recent.every((line) => {
			const lower = line.toLowerCase();
			return featKeywords.some((kw) => lower.includes(kw));
		});

		if (allFeats) {
			process.stderr.write(
				"[Refactor Suggestion] 直近5セッションが全て機能追加です。" +
					"`/refactor-session` でリファクタリングセッションを検討してください。\n",
			);
		}
	} catch (err) {
		process.stderr.write(
			`[Refactor Suggestion] check failed: ${err.message}\n`,
		);
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
		path.join(require("os").homedir(), ".claude", "agent-memory");
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

function detectBaseBranch() {
	try {
		const upstream = execSync(
			"git rev-parse --abbrev-ref @{upstream} 2>/dev/null",
			{
				encoding: "utf8",
				timeout: 2000,
			},
		).trim();
		return upstream.replace(/^origin\//, "");
	} catch {}
	try {
		const ref = execSync(
			"git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null",
			{
				encoding: "utf8",
				timeout: 2000,
			},
		).trim();
		return ref.replace(/^refs\/remotes\/origin\//, "");
	} catch {}
	return "main";
}

function loadBoundaries() {
	try {
		const currentBranch = execSync("git branch --show-current 2>/dev/null", {
			encoding: "utf8",
			timeout: 2000,
		}).trim();
		if (!currentBranch) return;

		const baseBranch = detectBaseBranch();
		if (currentBranch === baseBranch) return;

		// Check if there are commits ahead of base
		const aheadCount = execSync(
			`git log ${baseBranch}..HEAD --oneline 2>/dev/null | wc -l`,
			{ encoding: "utf8", timeout: 2000 },
		).trim();
		if (parseInt(aheadCount, 10) === 0) return;

		// Extract rejected() and constraint() lines from branch commits
		const bodies = execSync(
			`git log ${baseBranch}..HEAD --format="%b" 2>/dev/null`,
			{ encoding: "utf8", timeout: 2000 },
		);
		const boundaries = bodies
			.split("\n")
			.filter((line) => /^(rejected|constraint)\(/.test(line))
			.slice(0, 5);

		if (boundaries.length === 0) return;

		const lines = ["\u26a0\ufe0f Boundaries:"];
		for (const b of boundaries) {
			lines.push(`  ${b}`);
		}

		// stdout = additionalContext for Claude (agent MUST know these)
		process.stdout.write(lines.join("\n") + "\n");
	} catch {
		// Non-blocking — silently skip on any error
	}
}

// Read stdin and pass through
let data = "";
process.stdin.on("data", (chunk) => {
	data += chunk;
});
process.stdin.on("end", () => {
	// HANDOFF.md があればセッション状態の復元をスキップ（引き継ぎ情報で十分）
	const hasHandoff = loadHandoff();
	if (!hasHandoff) {
		checkHandoffRequest(); // HANDOFF.md がない場合のみチェック
		loadState();
	}

	// Load profile from last checkpoint or task-aware
	let profile = "task-aware";
	try {
		const cpPath = path.join(
			require("os").homedir(),
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
	snapshotActivePlans();
	loadFeatureList();
	loadProgressLog();
	suggestRefactorSession();
	suggestTestBaseline();
	runBaselineCheck();
	loadBoundaries();
	process.stdout.write(data);
});
