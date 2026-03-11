#!/usr/bin/env node
// Auto-format + lint files after Edit/Write
// Uses Rust-based tools for speed: Biome+Oxlint (TS/JS), Ruff (Python), gofmt (Go)
// Lint errors are injected as additionalContext to drive self-correction loop.
// Ref: Harness Engineering Best Practices 2026 — "Quality Loops (PostToolUse)"
//
// Triggered by: hooks.PostToolUse (Edit|Write)
const { execSync } = require("child_process");
const path = require("path");

// --- Tool resolution (cached at startup) ---
function whichSync(cmd) {
	try {
		return execSync(`which ${cmd}`, {
			stdio: "pipe",
			timeout: 3000,
			encoding: "utf8",
		}).trim();
	} catch (e) {
		process.stderr.write(`[Auto-Format] ${cmd} not found\n`);
		return null;
	}
}

const BIOME = whichSync("biome") ? "biome" : "npx --yes @biomejs/biome@latest";
const OXLINT = whichSync("oxlint") ? "oxlint" : "npx --yes oxlint@latest";
const RUFF = whichSync("ruff") || "ruff";
const GOFMT = whichSync("gofmt") || "gofmt";

// --- Helpers ---
function runCapture(cmd, timeout = 10000) {
	try {
		const out = execSync(cmd, {
			stdio: "pipe",
			timeout,
			encoding: "utf8",
			env: { ...process.env, NO_COLOR: "1" },
		});
		return { ok: true, output: out };
	} catch (e) {
		return { ok: false, output: (e.stdout || "") + (e.stderr || "") };
	}
}

function runSilent(cmd, timeout = 10000) {
	try {
		execSync(cmd, { stdio: "pipe", timeout });
		return true;
	} catch (e) {
		process.stderr.write(`[Auto-Format] cmd failed: ${cmd.split(" ")[0]}\n`);
		return false;
	}
}

function trimLines(text, max = 20) {
	return text
		.split("\n")
		.map((l) => l.trimEnd())
		.filter((l) => l)
		.slice(0, max);
}

// --- Per-language format + lint ---
function handleTypeScript(filePath) {
	const errors = [];
	// 1. Format (silent, auto-fix)
	runSilent(`${BIOME} format --write "${filePath}"`);
	// 2. Lint with auto-fix, capture remaining issues
	const { ok, output } = runCapture(
		`${OXLINT} --fix "${filePath}" 2>&1`,
		10000,
	);
	if (!ok && output) {
		const issues = trimLines(output).filter(
			(l) =>
				!l.startsWith("Found") &&
				!l.startsWith("Finished") &&
				!l.includes("oxlint"),
		);
		if (issues.length > 0) errors.push(...issues);
	}
	return errors;
}

function handlePython(filePath) {
	const errors = [];
	// 1. Format
	runSilent(`${RUFF} format "${filePath}"`);
	// 2. Lint with auto-fix, capture remaining issues
	const { ok, output } = runCapture(
		`${RUFF} check --fix "${filePath}" 2>&1`,
		10000,
	);
	if (!ok && output && !/All checks passed/.test(output)) {
		const issues = trimLines(output).filter((l) => !l.startsWith("Found"));
		if (issues.length > 0) errors.push(...issues);
	}
	return errors;
}

function handleGo(filePath) {
	const errors = [];
	// 1. Format
	runSilent(`${GOFMT} -w "${filePath}"`);
	// 2. Vet (fast, built-in)
	const dir = path.dirname(filePath);
	const { ok, output } = runCapture(`go vet "${dir}/..." 2>&1`, 15000);
	if (!ok && output) {
		const lines = trimLines(output);
		if (lines.length > 0) errors.push(...lines);
	}
	return errors;
}

// --- Main ---
function formatAndLint(filePath) {
	if (!filePath) return null;

	const ext = path.extname(filePath).toLowerCase();
	let errors = [];

	if (/^\.(tsx?|jsx?)$/.test(ext)) {
		errors = handleTypeScript(filePath);
	} else if (ext === ".py") {
		errors = handlePython(filePath);
	} else if (ext === ".go") {
		errors = handleGo(filePath);
	} else if (/^\.(json|jsonc|css|scss)$/.test(ext)) {
		runSilent(`${BIOME} format --write "${filePath}"`);
		return null;
	}

	return errors.length > 0 ? errors : null;
}

let data = "";
process.stdin.on("data", (chunk) => {
	data += chunk;
});
process.stdin.on("end", () => {
	try {
		const payload = JSON.parse(data);
		const filePath = payload?.tool_input?.file_path;
		const errors = formatAndLint(filePath);

		if (errors) {
			const ext = path.extname(filePath || "").toLowerCase();
			const tool = /^\.(tsx?|jsx?)$/.test(ext)
				? "Oxlint"
				: ext === ".py"
					? "Ruff"
					: ext === ".go"
						? "go vet"
						: "Linter";

			process.stderr.write(
				`[Auto-Lint] ${tool}: ${errors.length} issue(s) in ${path.basename(filePath)}\n`,
			);

			const ctx = [
				`[Auto-Lint] ${tool} が ${path.basename(filePath)} で問題を検出:`,
				"",
				...errors.map((e) => `  ${e}`),
				"",
				"FIX: 上記の lint エラーを修正してください。リンター設定は変更せず、コードを修正すること。",
			].join("\n");

			process.stdout.write(
				JSON.stringify({
					hookSpecificOutput: {
						hookEventName: "PostToolUse",
						additionalContext: ctx,
					},
				}),
			);
		} else {
			process.stderr.write(
				`[Auto-Format] OK: ${path.basename(filePath || "unknown")}\n`,
			);
			process.stdout.write(data);
		}
	} catch (e) {
		process.stderr.write(`[Auto-Format] parse error: ${e.message}\n`);
		process.stdout.write(data || "{}");
	}
});
