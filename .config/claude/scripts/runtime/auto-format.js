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
const GOLANGCI_LINT = whichSync("golangci-lint");

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

// --- Lint rule WHY/FIX guides (inline for speed) ---
// Ref: references/lint-rule-guides.md (full version)
const LINT_GUIDES = {
	// TypeScript/JavaScript (Oxlint)
	"no-explicit-any": {
		why: "型安全性の喪失 → GP-005 違反",
		fix: "unknown + type guard、ジェネリクス <T>、または具体型を使用",
	},
	"no-unused-vars": {
		why: "デッドコードは可読性低下とバンドルサイズ増加",
		fix: "未使用の変数・import を削除。意図的なら _ プレフィックス",
	},
	"no-console": {
		why: "プロダクションコードの console.log は情報漏洩リスク",
		fix: "logger を使用、またはデバッグ完了後に削除",
	},
	eqeqeq: {
		why: "== は暗黙の型変換で予期しない真偽値を返す",
		fix: "=== (厳密等価) を使用",
	},
	// Python (Ruff)
	E501: {
		why: "長すぎる行は可読性を著しく下げる",
		fix: "変数抽出、改行、文字列の分割",
	},
	F401: {
		why: "未使用 import はロード時間とメモリを浪費",
		fix: "import 行を削除",
	},
	F841: {
		why: "未使用変数はデッドコードの兆候",
		fix: "変数を使用するか _ で破棄",
	},
	E711: {
		why: "== None より is None が Python イディオム",
		fix: "is None / is not None を使用",
	},
	// Go (golangci-lint)
	errcheck: {
		why: "エラー戻り値の無視は silent failure — GP-004 違反",
		fix: 'if err != nil { return fmt.Errorf("...: %w", err) }',
	},
	gosec: {
		why: "セキュリティ脆弱性の自動検出",
		fix: "指摘に従いセキュアな代替手段を使用",
	},
};

function enrichWithGuide(errorLine) {
	for (const [rule, guide] of Object.entries(LINT_GUIDES)) {
		if (errorLine.includes(rule)) {
			return `${errorLine}\n    WHY: ${guide.why}\n    FIX: ${guide.fix}`;
		}
	}
	return errorLine;
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
	// 2. Lint — prefer golangci-lint if available, fallback to go vet
	const dir = path.dirname(filePath);
	if (GOLANGCI_LINT) {
		const { ok, output } = runCapture(
			`${GOLANGCI_LINT} run --fix --new-from-rev=HEAD "${dir}/..." 2>&1`,
			20000,
		);
		if (!ok && output) {
			const issues = trimLines(output).filter(
				(l) => !l.startsWith("level=") && !l.includes("congrats"),
			);
			if (issues.length > 0) errors.push(...issues);
		}
	} else {
		const { ok, output } = runCapture(`go vet "${dir}/..." 2>&1`, 15000);
		if (!ok && output) {
			const lines = trimLines(output);
			if (lines.length > 0) errors.push(...lines);
		}
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
				...errors.map((e) => `  ${enrichWithGuide(e)}`),
				"",
				"上記の lint エラーを修正してください。リンター設定は変更せず、コードを修正すること。",
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
