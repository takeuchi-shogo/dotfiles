#!/usr/bin/env node

/**
 * PreCompact hook: コンテキスト圧縮前に作業状態と圧縮ガイダンスを stdout に出力する。
 * Claude が圧縮時にこの情報を参照し、重要な状態を保持できる。
 *
 * OpenDev の多段コンテキスト圧縮戦略を参考に、
 * 圧縮時に何を保持し何を落とすべきかのガイダンスを提供する。
 */

const { execSync } = require("child_process");
const fs = require("fs");
const path = require("path");

function run(cmd) {
	try {
		return execSync(cmd, { encoding: "utf-8", timeout: 5000 }).trim();
	} catch {
		return "";
	}
}

// ── 1. Git state (既存) ──────────────────────────────────────────

const branch = run("git branch --show-current");
const diffStat = run("git diff --stat HEAD");
const stagedStat = run("git diff --cached --stat");
const untrackedFiles = run("git ls-files --others --exclude-standard");

// ── 2. Active plans detection ────────────────────────────────────

function findActivePlans() {
	const planDirs = ["docs/plans/active", "tmp/plans"];
	const plans = [];

	for (const dir of planDirs) {
		try {
			const files = fs.readdirSync(dir).filter((f) => f.endsWith(".md"));
			for (const file of files) {
				const content = fs.readFileSync(path.join(dir, file), "utf-8");
				const pending = (content.match(/^- \[ \]/gm) || []).length;
				const done = (content.match(/^- \[x\]/gim) || []).length;
				if (pending > 0) {
					// Extract goal line
					const goalMatch = content.match(/## Goal\s*\n(.+)/);
					const goal = goalMatch ? goalMatch[1].trim() : "(no goal)";
					plans.push({
						file: `${dir}/${file}`,
						goal,
						progress: `${done}/${done + pending}`,
						pending,
					});
				}
			}
		} catch {
			// Directory doesn't exist — skip
		}
	}
	return plans;
}

// ── 3. Recent offloaded outputs ──────────────────────────────────

function findRecentOffloads() {
	const offloadDir = "/tmp/claude-tool-outputs";
	try {
		const files = fs.readdirSync(offloadDir);
		return files
			.map((f) => {
				const stat = fs.statSync(path.join(offloadDir, f));
				return { file: f, size: stat.size, mtime: stat.mtimeMs };
			})
			.sort((a, b) => b.mtime - a.mtime)
			.slice(0, 5)
			.map((f) => `${f.file} (${Math.round(f.size / 1024)}KB)`);
	} catch {
		return [];
	}
}

// ── 4. Build compaction guidance ─────────────────────────────────

const activePlans = findActivePlans();
const recentOffloads = findRecentOffloads();

const state = {
	timestamp: new Date().toISOString(),
	git: {
		branch: branch || "(detached)",
		uncommitted_changes: diffStat || "(none)",
		staged_changes: stagedStat || "(none)",
		untracked_files: untrackedFiles
			? untrackedFiles.split("\n").slice(0, 20)
			: [],
	},
	active_plans: activePlans,
	recent_offloads: recentOffloads,
};

// ── 5. Compaction guidance (保持優先度) ──────────────────────────

const guidance = [
	"## Compaction Guidance (圧縮時の保持優先度)",
	"",
	"### MUST KEEP (絶対に保持):",
	"- 現在のタスクの目標と進捗状況",
	"- ユーザーからの最新の指示・フィードバック",
	"- アクティブなプランの未完了ステップ",
	"- 直近のエラーとその解決策",
	"- 重要な意思決定とその理由",
	"",
	"### SHOULD KEEP (可能な限り保持):",
	"- 直近 3 ターンの会話コンテキスト",
	"- 変更したファイルのパスと変更理由",
	"- 現在のブランチとコミット状況",
	"",
	"### CAN DROP (圧縮可能):",
	"- 古いツール出力の詳細（ファイルリスト、grep 結果等）",
	"- 完了済みの中間ステップの詳細",
	"- エージェントからの詳細レポート（要約のみ保持）",
	"- 探索的な検索結果（必要なら再検索可能）",
];

if (activePlans.length > 0) {
	guidance.push("");
	guidance.push("### Active Plans (圧縮後も追跡必須):");
	for (const plan of activePlans) {
		guidance.push(
			`- ${plan.file}: ${plan.goal} [${plan.progress} complete, ${plan.pending} remaining]`,
		);
	}
}

if (recentOffloads.length > 0) {
	guidance.push("");
	guidance.push(
		"### Offloaded Outputs (Read で再取得可能 — 圧縮時に詳細は不要):",
	);
	for (const f of recentOffloads) {
		guidance.push(`- /tmp/claude-tool-outputs/${f}`);
	}
}

state.compaction_guidance = guidance.join("\n");

// ── 6. Force checkpoint before compaction ────────────────────────

try {
	execSync('python3 $HOME/.claude/scripts/checkpoint_manager.py <<< "{}"', {
		encoding: "utf-8",
		timeout: 10000,
		stdio: ["pipe", "pipe", "pipe"],
	});
} catch {
	// Non-critical — checkpoint failure shouldn't block compaction
}

console.log(JSON.stringify(state, null, 2));
