#!/usr/bin/env node
"use strict";

/**
 * System Prompt Patcher — Claude Code CLI バンドルにパッチを適用
 *
 * 仕組み:
 * 1. npm root -g で Claude Code のグローバルインストール先を自動検出
 * 2. バンドルファイル (cli.mjs, cli.js 等) を探す
 * 3. バックアップを作成 (.bak)
 * 4. patches/{versionBucket}/ から .find.txt/.replace.txt ペアを読み込み
 * 5. variable-aware regex でミニファイされた変数名の変更を吸収してパッチ適用
 */

const fs = require("fs");
const path = require("path");
const { execSync } = require("child_process");

// ──────────────────────────────────────
// ユーティリティ
// ──────────────────────────────────────

/** コマンドを実行して stdout を文字列で返す */
function run(cmd) {
	return execSync(cmd, { encoding: "utf-8" }).trim();
}

/**
 * バージョン文字列をバケット化
 * "2.1.76" → "2.1.x"
 */
function toBucket(version) {
	const parts = version.replace(/^v/, "").split(".");
	if (parts.length < 2) {
		throw new Error(`不正なバージョン形式: ${version}`);
	}
	return `${parts[0]}.${parts[1]}.x`;
}

/**
 * find テキスト内の {{VAR}} プレースホルダーを \w+ に展開し、
 * それ以外のメタ文字をエスケープした正規表現を返す。
 *
 * また、連続する空白を \s+ に置換してミニファイ差異を吸収する。
 */
function buildVariableAwareRegex(findText) {
	// {{VAR}} を一時トークンに置き換え
	const placeholder = "\0VAR\0";
	const placeholderRe = /\{\{[A-Z_][A-Z0-9_]*\}\}/g;
	const tokens = [];
	let temp = findText.replace(placeholderRe, () => {
		tokens.push(placeholder);
		return placeholder;
	});

	// 正規表現メタ文字をエスケープ（プレースホルダー以外）
	const escaped = temp.replace(/[.*+?^${}()|[\]\\]/g, (ch) => {
		// プレースホルダー中の \0 はスキップ
		return `\\${ch}`;
	});

	// 連続空白を \s+ に置換（ミニファイ差異の吸収）
	let pattern = escaped.replace(/\s+/g, "\\s+");

	// プレースホルダーを \w+ に復元
	pattern = pattern.split(escapeForSplit(placeholder)).join("(\\w+)");

	return new RegExp(pattern, "g");
}

/** split 用にメタ文字をエスケープ */
function escapeForSplit(str) {
	return str.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

// ──────────────────────────────────────
// メイン処理
// ──────────────────────────────────────

function main() {
	console.log("🔍 Claude Code バンドルを検出中...");

	// Claude Code のバージョンを取得
	let version;
	try {
		const rawVersion = run("claude --version");
		// "claude v2.1.76" のような出力からバージョン部分を抽出
		const match = rawVersion.match(/(\d+\.\d+\.\d+)/);
		if (!match) {
			throw new Error(`バージョンが検出できません: ${rawVersion}`);
		}
		version = match[1];
	} catch (e) {
		console.error("❌ claude --version の実行に失敗:", e.message);
		process.exit(1);
	}

	const bucket = toBucket(version);
	console.log(`📦 Claude Code v${version} (バケット: ${bucket})`);

	// npm root -g でグローバルパッケージのルートを取得
	let npmRoot;
	try {
		npmRoot = run("npm root -g");
	} catch (e) {
		console.error("❌ npm root -g の実行に失敗:", e.message);
		process.exit(1);
	}

	// Claude Code バンドルファイルを探す
	const claudeDir = path.join(npmRoot, "@anthropic-ai", "claude-code");
	if (!fs.existsSync(claudeDir)) {
		console.error(`❌ Claude Code パッケージが見つかりません: ${claudeDir}`);
		process.exit(1);
	}

	// バンドル候補を優先度順で探す
	const bundleCandidates = ["cli.mjs", "cli.js", "dist/cli.mjs", "dist/cli.js"];
	let bundlePath = null;

	for (const candidate of bundleCandidates) {
		const full = path.join(claudeDir, candidate);
		if (fs.existsSync(full)) {
			bundlePath = full;
			break;
		}
	}

	if (!bundlePath) {
		console.error(
			"❌ バンドルファイルが見つかりません。候補:",
			bundleCandidates.join(", "),
		);
		process.exit(1);
	}

	console.log(`📄 バンドル: ${bundlePath}`);

	// パッチディレクトリを探す
	const patchesDir = path.join(__dirname, "patches", bucket);
	if (!fs.existsSync(patchesDir)) {
		console.log(`⚠️  パッチディレクトリが見つかりません: ${patchesDir}`);
		console.log(`   patches/${bucket}/ にパッチファイルを配置してください。`);
		process.exit(0);
	}

	// .find.txt ファイルを収集してソート
	const findFiles = fs
		.readdirSync(patchesDir)
		.filter((f) => f.endsWith(".find.txt"))
		.sort();

	if (findFiles.length === 0) {
		console.log("⚠️  適用するパッチがありません。");
		process.exit(0);
	}

	console.log(`🩹 ${findFiles.length} 個のパッチを検出`);

	// バックアップ作成
	const backupPath = bundlePath + ".bak";
	if (!fs.existsSync(backupPath)) {
		fs.copyFileSync(bundlePath, backupPath);
		console.log(`💾 バックアップ作成: ${backupPath}`);
	} else {
		console.log(`💾 バックアップ既存: ${backupPath}`);
	}

	// バンドルを読み込み
	let content = fs.readFileSync(bundlePath, "utf-8");
	const originalSize = Buffer.byteLength(content, "utf-8");
	let appliedCount = 0;
	let skippedCount = 0;

	// パッチを順番に適用
	for (const findFile of findFiles) {
		const baseName = findFile.replace(".find.txt", "");
		const replaceFile = baseName + ".replace.txt";
		const replacePath = path.join(patchesDir, replaceFile);

		const findText = fs
			.readFileSync(path.join(patchesDir, findFile), "utf-8")
			.trim();

		// replace ファイルが無ければ空文字（= 削除）
		let replaceText = "";
		if (fs.existsSync(replacePath)) {
			replaceText = fs.readFileSync(replacePath, "utf-8").trim();
		}

		if (!findText) {
			console.log(`  ⏭️  ${baseName}: find テキストが空、スキップ`);
			skippedCount++;
			continue;
		}

		// variable-aware regex を構築してマッチ
		const regex = buildVariableAwareRegex(findText);
		const matches = content.match(regex);

		if (!matches || matches.length === 0) {
			console.log(`  ⏭️  ${baseName}: マッチなし、スキップ`);
			skippedCount++;
			continue;
		}

		content = content.replace(regex, replaceText);
		appliedCount++;
		console.log(`  ✅ ${baseName}: 適用 (${matches.length} 箇所)`);
	}

	// 結果を書き込み
	if (appliedCount > 0) {
		fs.writeFileSync(bundlePath, content, "utf-8");
		const newSize = Buffer.byteLength(content, "utf-8");
		const reduction = originalSize - newSize;
		const percent = ((reduction / originalSize) * 100).toFixed(2);

		console.log("");
		console.log("📊 結果:");
		console.log(`   適用: ${appliedCount} / スキップ: ${skippedCount}`);
		console.log(`   元サイズ: ${originalSize.toLocaleString()} bytes`);
		console.log(`   新サイズ: ${newSize.toLocaleString()} bytes`);
		console.log(`   削減: ${reduction.toLocaleString()} bytes (${percent}%)`);
		console.log("");
		console.log("✅ パッチ適用完了。verify-patch.js で検証してください。");
	} else {
		console.log("");
		console.log(
			"ℹ️  適用されたパッチはありません。バンドルは変更されていません。",
		);
	}
}

main();
