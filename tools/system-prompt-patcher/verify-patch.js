#!/usr/bin/env node
"use strict";

/**
 * System Prompt Patch Verifier — パッチ適用後の Claude Code CLI を検証
 *
 * 検証項目:
 * 1. `claude --version` が正常に動作するか
 * 2. `claude --help` が正常出力するか
 * 3. パッチ前後のファイルサイズ比較
 * 4. 失敗時はバックアップから自動復元
 */

const fs = require("fs");
const path = require("path");
const { execSync } = require("child_process");

// ──────────────────────────────────────
// ユーティリティ
// ──────────────────────────────────────

/** コマンドを実行して stdout を返す。失敗時は null */
function tryRun(cmd, timeoutMs) {
	try {
		return execSync(cmd, {
			encoding: "utf-8",
			timeout: timeoutMs || 15000,
			stdio: ["pipe", "pipe", "pipe"],
		}).trim();
	} catch {
		return null;
	}
}

// ──────────────────────────────────────
// バンドルパス検出（patch-cli.js と同じロジック）
// ──────────────────────────────────────

function findBundlePath() {
	let npmRoot;
	try {
		npmRoot = execSync("npm root -g", { encoding: "utf-8" }).trim();
	} catch {
		return null;
	}

	const claudeDir = path.join(npmRoot, "@anthropic-ai", "claude-code");
	if (!fs.existsSync(claudeDir)) return null;

	const candidates = ["cli.mjs", "cli.js", "dist/cli.mjs", "dist/cli.js"];
	for (const c of candidates) {
		const full = path.join(claudeDir, c);
		if (fs.existsSync(full)) return full;
	}
	return null;
}

// ──────────────────────────────────────
// 復元処理
// ──────────────────────────────────────

function restore(bundlePath, backupPath) {
	if (!fs.existsSync(backupPath)) {
		console.error("❌ バックアップが存在しません。手動で復元してください。");
		console.error(`   期待パス: ${backupPath}`);
		return false;
	}

	try {
		fs.copyFileSync(backupPath, bundlePath);
		console.log(
			`🔄 バックアップから復元しました: ${backupPath} → ${bundlePath}`,
		);
		return true;
	} catch (e) {
		console.error("❌ 復元に失敗:", e.message);
		return false;
	}
}

// ──────────────────────────────────────
// メイン検証
// ──────────────────────────────────────

function main() {
	console.log("🔍 パッチ検証を開始...");
	console.log("");

	const bundlePath = findBundlePath();
	if (!bundlePath) {
		console.error("❌ Claude Code バンドルが見つかりません。");
		process.exit(1);
	}

	const backupPath = bundlePath + ".bak";
	const hasBackup = fs.existsSync(backupPath);
	const results = [];
	let failed = false;

	// ── 検証 1: claude --version ──
	console.log("📋 検証 1/3: claude --version");
	const versionOutput = tryRun("claude --version");
	if (versionOutput && /\d+\.\d+\.\d+/.test(versionOutput)) {
		console.log(`   ✅ 正常: ${versionOutput}`);
		results.push({ name: "version", pass: true });
	} else {
		console.log(`   ❌ 失敗: ${versionOutput || "(出力なし)"}`);
		results.push({ name: "version", pass: false });
		failed = true;
	}

	// ── 検証 2: claude --help ──
	console.log("📋 検証 2/3: claude --help");
	const helpOutput = tryRun("claude --help");
	if (helpOutput && helpOutput.length > 50) {
		// --help の出力が十分な長さかチェック
		const lines = helpOutput.split("\n").length;
		console.log(`   ✅ 正常: ${lines} 行の出力`);
		results.push({ name: "help", pass: true });
	} else {
		console.log(
			`   ❌ 失敗: 出力が短すぎます (${helpOutput ? helpOutput.length : 0} 文字)`,
		);
		results.push({ name: "help", pass: false });
		failed = true;
	}

	// ── 検証 3: ファイルサイズ比較 ──
	console.log("📋 検証 3/3: ファイルサイズ比較");
	const currentSize = fs.statSync(bundlePath).size;

	if (hasBackup) {
		const backupSize = fs.statSync(backupPath).size;
		const diff = backupSize - currentSize;
		const percent = ((diff / backupSize) * 100).toFixed(2);

		if (diff > 0) {
			console.log(`   ✅ 削減: ${diff.toLocaleString()} bytes (${percent}%)`);
			console.log(`      元: ${backupSize.toLocaleString()} bytes`);
			console.log(`      現: ${currentSize.toLocaleString()} bytes`);
		} else if (diff === 0) {
			console.log("   ℹ️  サイズ変更なし（パッチ未適用の可能性）");
		} else {
			console.log(`   ⚠️  サイズ増加: ${Math.abs(diff).toLocaleString()} bytes`);
		}
		results.push({ name: "size", pass: true });
	} else {
		console.log("   ℹ️  バックアップなし — サイズ比較をスキップ");
		console.log(`      現サイズ: ${currentSize.toLocaleString()} bytes`);
		results.push({ name: "size", pass: true, skipped: true });
	}

	// ── 結果サマリ ──
	console.log("");
	console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");

	if (failed) {
		console.log("❌ 検証失敗 — パッチに問題があります。");

		if (hasBackup) {
			console.log("");
			console.log("🔄 バックアップから自動復元を試みます...");
			const restored = restore(bundlePath, backupPath);

			if (restored) {
				// 復元後に再検証
				console.log("");
				console.log("🔍 復元後の再検証...");
				const recheck = tryRun("claude --version");
				if (recheck && /\d+\.\d+\.\d+/.test(recheck)) {
					console.log(`   ✅ 復元成功: ${recheck}`);
				} else {
					console.log("   ❌ 復元後も問題あり。手動確認が必要です。");
				}
			}
		} else {
			console.log("⚠️  バックアップがないため自動復元できません。");
		}

		process.exit(1);
	}

	console.log("✅ 全検証パス — パッチは正常に動作しています。");

	if (hasBackup) {
		console.log("");
		console.log("💡 ヒント: バックアップを削除するには:");
		console.log(`   rm "${backupPath}"`);
	}
}

main();
