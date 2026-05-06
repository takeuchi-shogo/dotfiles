#!/usr/bin/env node

/**
 * PostCompact hook: コンテキスト圧縮後の検証とメモリ gardening プロンプト。
 *
 * Context Constitution P3 (Proactive > Reactive) の実装:
 * - アクティブ Plan の存在リマインダー
 * - compaction 回数に応じた session health 判定
 * - メモリ gardening プロンプト（2回目以降）
 */

const fs = require("fs");
const path = require("path");
const { execSync } = require("child_process");

const SESSION_STATE_DIR =
	process.env.CLAUDE_SESSION_STATE_DIR ||
	path.join(process.env.HOME, ".claude", "session-state");

const COMPACTION_COUNTER_FILE = path.join(
	SESSION_STATE_DIR,
	"compaction-counter.json",
);

const RECENTLY_EDITED_LIMIT = 8;

// ── 1. Read compaction counter ──────────────────────────────────

function getCompactionCount() {
	try {
		const data = JSON.parse(fs.readFileSync(COMPACTION_COUNTER_FILE, "utf8"));
		if (Date.now() - data.lastReset > 2 * 60 * 60 * 1000) {
			return 0;
		}
		return data.count || 0;
	} catch {
		return 0;
	}
}

// ── 2. Find active plans ────────────────────────────────────────

function findActivePlans() {
	const planDirs = ["docs/plans/active", "tmp/plans"];
	const plans = [];

	for (const dir of planDirs) {
		try {
			const files = fs.readdirSync(dir).filter((f) => f.endsWith(".md"));
			for (const file of files) {
				const content = fs.readFileSync(path.join(dir, file), "utf-8");
				const pending = (content.match(/^- \[ \]/gm) || []).length;
				if (pending > 0) {
					plans.push(`${dir}/${file}`);
				}
			}
		} catch {
			// Directory doesn't exist
		}
	}
	return plans;
}

// ── 2b. Find recently edited files (re-injection selector) ──────
//
// Re-injection policy: tool 出力を全部戻すのではなく、「次の発話で必要になる
// 高確率のシグナル」だけを優先注入する。git の作業ツリーに残っている変更ファイル
// は、compaction 直後でも「直前まで触っていた」可能性が高い。

function findRecentlyEditedFiles() {
	try {
		const out = execSync("git diff --name-only HEAD 2>/dev/null", {
			encoding: "utf-8",
			timeout: 5000,
		});
		const files = out
			.split("\n")
			.map((s) => s.trim())
			.filter((s) => s.length > 0);
		return files.slice(0, RECENTLY_EDITED_LIMIT);
	} catch {
		return [];
	}
}

// ── 3. Build verification output ────────────────────────────────

const count = getCompactionCount();
const activePlans = findActivePlans();
const recentlyEdited = findRecentlyEditedFiles();
const output = [];

output.push(`[PostCompact] Compaction #${count} completed.`);

// Re-injection Priority (P3 selector policy)
if (activePlans.length > 0 || recentlyEdited.length > 0) {
	output.push("");
	output.push("## Re-injection Priority (highest first)");
}

// P1: Active plans
if (activePlans.length > 0) {
	output.push("");
	output.push("### P1 Active Plans (re-ground after compaction):");
	for (const plan of activePlans) {
		output.push(`- Read \`${plan}\` to restore task context`);
	}
}

// P2: Recently edited working-tree files
if (recentlyEdited.length > 0) {
	output.push("");
	output.push("### P2 Recently Edited Files (working tree, uncommitted):");
	for (const file of recentlyEdited) {
		output.push(`- \`${file}\``);
	}
}

// Memory gardening prompt (P3: Proactive)
if (count >= 2) {
	output.push("");
	output.push("## 🌱 Memory Gardening Checkpoint");
	output.push(
		"このセッションで以下に該当する知見があれば memory/ に保存してください:",
	);
	output.push("- 重要な意思決定とその理由（なぜ A を選び B を捨てたか）");
	output.push("- 試して失敗したアプローチ（Dead Ends）");
	output.push("- ユーザーから受けたフィードバック・方針変更");
	output.push("- 発見した非自明なコードベースの制約");
}

// Session health
if (count >= 4) {
	output.push("");
	output.push(`## ⚠ Session Health: ${count} compactions`);
	output.push(
		"コンテキスト品質の劣化リスクが高い。`/checkpoint` → 新セッション推奨。",
	);
}

// Compact log
const logLine = `[${new Date().toISOString()}] PostCompact: compaction #${count}, plans=${activePlans.length}\n`;
try {
	fs.appendFileSync("/tmp/claude-compact.log", logLine);
} catch {
	// Non-critical
}

console.log(output.join("\n"));
