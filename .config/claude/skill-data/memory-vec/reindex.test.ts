// reindex.test.ts — readSourceFiles の複数ルート収集 + source タグのユニットテスト。
// 実行: node --experimental-strip-types --test reindex.test.ts

import { test } from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync, mkdirSync, writeFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { readSourceFiles } from "./reindex.ts";

test("readSourceFiles collects md from multiple roots with source tags", () => {
	const base = mkdtempSync(join(tmpdir(), "mvtest-"));
	const memRoot = join(base, "memory");
	const vaultRoot = join(base, "05-Literature");
	mkdirSync(memRoot);
	mkdirSync(vaultRoot);
	writeFileSync(join(memRoot, "a.md"), "memory note a");
	writeFileSync(join(vaultRoot, "lit-x.md"), "literature note x");
	writeFileSync(join(vaultRoot, "ignore.txt"), "not markdown");

	const docs = readSourceFiles([
		{ root: memRoot, source: "memory" },
		{ root: vaultRoot, source: "vault" },
	]);

	const byName = Object.fromEntries(docs.map((d) => [d.name, d]));
	assert.equal(docs.length, 2);
	assert.equal(byName["a.md"].source, "memory");
	assert.equal(byName["lit-x.md"].source, "vault");
	assert.ok(!("ignore.txt" in byName));
	rmSync(base, { recursive: true, force: true });
});

test("readSourceFiles skips missing roots gracefully", () => {
	const docs = readSourceFiles([
		{ root: "/nonexistent/path/xyz", source: "vault" },
	]);
	assert.deepEqual(docs, []);
});
