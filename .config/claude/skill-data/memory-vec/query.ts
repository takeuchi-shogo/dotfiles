// query.ts (Phase D)
//
// CLI: node --experimental-strip-types query.ts <query-text>
// Outputs JSON array on stdout: [{ path, name, distance }, ...]
//
// Located alongside node_modules/ (same reason as reindex.ts).

import { DatabaseSync } from "node:sqlite";
import * as sqliteVec from "sqlite-vec";
import { homedir } from "node:os";
import { join } from "node:path";
import { pipeline, env } from "@xenova/transformers";

env.allowLocalModels = false;
env.useBrowserCache = false;

const DB_PATH = join(homedir(), ".claude/skill-data/memory-vec/index.db");
const EMBED_MODEL = "Xenova/all-MiniLM-L6-v2";
const TOP_K = 5;

function openDB(path: string): DatabaseSync {
	const db = new DatabaseSync(path, { allowExtension: true });
	db.enableLoadExtension(true);
	sqliteVec.load(db);
	db.enableLoadExtension(false);
	return db;
}

let extractor: Awaited<ReturnType<typeof pipeline>> | null = null;

async function embed(text: string): Promise<Float32Array> {
	if (!extractor) {
		extractor = await pipeline("feature-extraction", EMBED_MODEL);
	}
	const out = (await extractor(text, {
		pooling: "mean",
		normalize: true,
	})) as unknown as { data: Float32Array };
	return new Float32Array(out.data);
}

async function main(): Promise<void> {
	const query = process.argv[2];
	if (!query || !query.trim()) {
		process.exit(2);
	}

	const db = openDB(DB_PATH);
	try {
		const qEmb = await embed(query);
		const blob = new Uint8Array(qEmb.buffer, qEmb.byteOffset, qEmb.byteLength);
		const rows = db
			.prepare(
				`SELECT d.name, d.path, v.distance
         FROM doc_vec AS v
         JOIN docs AS d ON d.id = v.rowid
         WHERE v.embedding MATCH ? AND v.k = ?
         ORDER BY v.distance ASC
         LIMIT ?`,
			)
			.all(blob, TOP_K, TOP_K) as {
			name: string;
			path: string;
			distance: number;
		}[];

		process.stdout.write(
			JSON.stringify(
				rows.map((r) => ({
					path: r.path,
					name: r.name,
					distance: r.distance,
				})),
			),
		);
	} finally {
		db.close();
	}
}

main().catch((e: unknown) => {
	process.stderr.write(`memory-vec-query: ${String(e)}\n`);
	process.exit(1);
});
