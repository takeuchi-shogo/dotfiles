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
const OVERFETCH_K = 20;

export function openDB(path: string): DatabaseSync {
	const db = new DatabaseSync(path, { allowExtension: true });
	db.enableLoadExtension(true);
	sqliteVec.load(db);
	db.enableLoadExtension(false);
	return db;
}

let extractor: Awaited<ReturnType<typeof pipeline>> | null = null;

export async function embed(text: string): Promise<Float32Array> {
	if (!extractor) {
		extractor = await pipeline("feature-extraction", EMBED_MODEL);
	}
	const out = (await extractor(text, {
		pooling: "mean",
		normalize: true,
	})) as unknown as { data: Float32Array };
	return new Float32Array(out.data);
}

export type QueryRow = {
	path: string;
	name: string;
	distance: number;
	source: string;
};

export async function queryIndex(
	dbPath: string,
	query: string,
	opts: { source?: string },
): Promise<QueryRow[]> {
	const db = openDB(dbPath);
	try {
		const qEmb = await embed(query);
		const blob = new Uint8Array(qEmb.buffer, qEmb.byteOffset, qEmb.byteLength);
		const rows = db
			.prepare(
				`SELECT d.name, d.path, d.source, v.distance
         FROM doc_vec AS v
         JOIN docs AS d ON d.id = v.rowid
         WHERE v.embedding MATCH ? AND v.k = ?
         ORDER BY v.distance ASC`,
			)
			.all(blob, OVERFETCH_K) as QueryRow[];
		const filtered = opts.source
			? rows.filter((r) => r.source === opts.source)
			: rows;
		return filtered.slice(0, TOP_K);
	} finally {
		db.close();
	}
}

async function main(): Promise<void> {
	const query = process.argv[2];
	if (!query || !query.trim()) {
		process.exit(2);
	}
	const srcIdx = process.argv.indexOf("--source");
	const source = srcIdx >= 0 ? process.argv[srcIdx + 1] : undefined;
	const rows = await queryIndex(DB_PATH, query, { source });
	process.stdout.write(JSON.stringify(rows));
}

if (import.meta.main) {
	main().catch((e: unknown) => {
		process.stderr.write(`memory-vec-query: ${String(e)}\n`);
		process.exit(1);
	});
}
