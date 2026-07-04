import { test } from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { openDB, embed, queryIndex } from "./query.ts";

type FixtureDoc = { name: string; path: string; body: string; source: string };

async function buildFixtureIndex(
	dbPath: string,
	docs: FixtureDoc[],
): Promise<void> {
	const db = openDB(dbPath);
	try {
		db.exec(
			`CREATE TABLE docs (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, path TEXT NOT NULL, body TEXT NOT NULL, source TEXT NOT NULL);`,
		);
		db.exec(`CREATE VIRTUAL TABLE doc_vec USING vec0(embedding FLOAT[384]);`);
		const insDoc = db.prepare(
			`INSERT INTO docs (name, path, body, source) VALUES (?, ?, ?, ?) RETURNING id`,
		);
		const insVec = db.prepare(
			`INSERT INTO doc_vec (rowid, embedding) VALUES (?, ?)`,
		);
		for (const d of docs) {
			const emb = await embed(d.body);
			const r = insDoc.get(d.name, d.path, d.body, d.source) as { id: number };
			insVec.run(
				BigInt(r.id),
				new Uint8Array(emb.buffer, emb.byteOffset, emb.byteLength),
			);
		}
	} finally {
		db.close();
	}
}

test("queryIndex returns source field and filters by source", async () => {
	const base = mkdtempSync(join(tmpdir(), "mvq-"));
	const dbPath = join(base, "index.db");
	await buildFixtureIndex(dbPath, [
		{
			name: "m.md",
			path: "/m.md",
			body: "go concurrency goroutine channel",
			source: "memory",
		},
		{
			name: "v.md",
			path: "/v.md",
			body: "go concurrency goroutine channel",
			source: "vault",
		},
	]);

	const all = await queryIndex(dbPath, "go concurrency", {});
	assert.ok(all.length >= 1);
	assert.ok(all.every((r) => typeof r.source === "string"));
	assert.ok(all.some((r) => r.source === "vault"));

	const memOnly = await queryIndex(dbPath, "go concurrency", {
		source: "memory",
	});
	assert.ok(memOnly.length >= 1);
	assert.ok(memOnly.every((r) => r.source === "memory"));

	const trailing = await queryIndex(dbPath, "go concurrency", {
		source: "memory, ",
	});
	assert.ok(trailing.length >= 1);
	assert.ok(trailing.every((r) => r.source === "memory"));

	const multi = await queryIndex(dbPath, "go concurrency", {
		source: "memory,vault",
	});
	assert.ok(multi.some((r) => r.source === "memory"));
	assert.ok(multi.some((r) => r.source === "vault"));
	assert.ok(multi.every((r) => r.source === "memory" || r.source === "vault"));

	rmSync(base, { recursive: true, force: true });
});
