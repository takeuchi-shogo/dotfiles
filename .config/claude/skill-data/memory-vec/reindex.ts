// reindex.ts (Phase C, post-review hardened)
//
// Full rebuild of ./index.db from memory/*.md with the following safeguards
// (added after multi-reviewer pass that flagged CRITICAL/HIGH risks):
//
//   - Single-flight via .reindex.lock (CRITICAL: concurrent DROP TABLE race)
//   - Atomic rebuild via index.db.tmp -> rename (CRITICAL: empty-DB residue
//     when DDL succeeds but population fails)
//   - Sentinel touch even on failure (CRITICAL: infinite retry loop when
//     rebuild fails before utimes)
//   - Per-file try/catch (HIGH: one unreadable file kills entire reindex)
//   - clean === "" skip (HIGH: zero-vector pollution from over-redacted file)
//   - redact_with_stats anomaly detection (HIGH: dead-code wrapper, no
//     defense-in-depth signal)
//   - Log stack/error with redact() applied (HIGH: traceback leaks raw text)
//
// Located alongside node_modules/ so ESM resolver finds @xenova/transformers
// and sqlite-vec without NODE_PATH gymnastics.

import { DatabaseSync } from "node:sqlite";
import * as sqliteVec from "sqlite-vec";
import {
	appendFileSync,
	closeSync,
	existsSync,
	mkdirSync,
	openSync,
	readdirSync,
	readFileSync,
	renameSync,
	rmSync,
	statSync,
	utimesSync,
} from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";
import { execFileSync } from "node:child_process";
import { performance } from "node:perf_hooks";
import { pipeline, env } from "@xenova/transformers";

env.allowLocalModels = false;
env.useBrowserCache = false;

const HOME = homedir();
const MEMORY_DIR = join(
	HOME,
	".claude/projects/-Users-takeuchishougo-dotfiles/memory",
);
const SKILL_DATA = join(HOME, ".claude/skill-data/memory-vec");
const DB_PATH = join(SKILL_DATA, "index.db");
const DB_TMP = join(SKILL_DATA, "index.db.tmp");
const LOCK_PATH = join(SKILL_DATA, ".reindex.lock");
const LOG_FILE = join(HOME, ".claude/logs/memory-vec.log");
const REDACTOR_LIB = join(SKILL_DATA, "lib");
const EMBED_MODEL = "Xenova/all-MiniLM-L6-v2";
const DIM = 384;
const ANOMALY_BYTES_FLOOR = 1024;
const STALE_LOCK_SEC = 600;

mkdirSync(SKILL_DATA, { recursive: true });

const REDACT_SCRUB_HELPER = `
import sys
sys.path.insert(0, ${JSON.stringify(REDACTOR_LIB)})
from memory_redactor import redact_for_embedding
sys.stdout.write(redact_for_embedding(sys.stdin.read()))
`;

function scrubForLog(text: string): string {
	// Best-effort redaction of error/traceback text via the same helper used
	// for embedding input. Failure leaves the original (logging is best-effort).
	try {
		return execFileSync("python3", ["-c", REDACT_SCRUB_HELPER], {
			input: text,
			encoding: "utf8",
			maxBuffer: 1 * 1024 * 1024,
			timeout: 1500,
		});
	} catch {
		return text.length > 500 ? `${text.slice(0, 500)}... [truncated]` : text;
	}
}

function logFailure(stage: string, err: unknown): void {
	try {
		mkdirSync(join(HOME, ".claude/logs"), { recursive: true });
		const errMsg =
			err instanceof Error ? `${err.name}: ${err.message}` : String(err);
		const stack = err instanceof Error && err.stack ? err.stack : undefined;
		const entry = {
			ts: new Date().toISOString(),
			source: "memory-vec-reindex",
			stage,
			error: scrubForLog(errMsg),
			stack: stack ? scrubForLog(stack) : undefined,
		};
		appendFileSync(LOG_FILE, JSON.stringify(entry) + "\n", "utf8");
	} catch (logErr) {
		process.stderr.write(
			`memory-vec-reindex: log write failed: ${String(logErr)}\n`,
		);
	}
}

type LockHandle = { fd: number };

function acquireLock(): LockHandle | null {
	// Reap stale lock (process killed mid-reindex)
	if (existsSync(LOCK_PATH)) {
		try {
			const ageSec = (Date.now() - statSync(LOCK_PATH).mtimeMs) / 1000;
			if (ageSec > STALE_LOCK_SEC) {
				rmSync(LOCK_PATH, { force: true });
			}
		} catch (e) {
			logFailure("lock_stale_check", e);
		}
	}
	try {
		const fd = openSync(LOCK_PATH, "wx");
		return { fd };
	} catch (e) {
		if ((e as NodeJS.ErrnoException).code === "EEXIST") {
			return null;
		}
		logFailure("lock_acquire", e);
		return null;
	}
}

function releaseLock(lock: LockHandle): void {
	try {
		closeSync(lock.fd);
	} catch (e) {
		logFailure("lock_close", e);
	}
	try {
		rmSync(LOCK_PATH, { force: true });
	} catch (e) {
		logFailure("lock_remove", e);
	}
}

function touchSentinel(target: string): void {
	// Touch DB mtime so the Stop hook treats the index as "freshly attempted",
	// even on failure — prevents infinite retry when memory mtime > db mtime.
	try {
		if (existsSync(target)) {
			const now = new Date();
			utimesSync(target, now, now);
		}
	} catch (e) {
		logFailure("touch_sentinel", e);
	}
}

const REDACT_HELPER = `
import sys
sys.path.insert(0, ${JSON.stringify(REDACTOR_LIB)})
from memory_redactor import redact_with_stats
text = sys.stdin.read()
stats = redact_with_stats(text)
sys.stdout.write(f"{stats.redaction_count}\\t{stats.bytes_in}\\t{stats.bytes_out}\\n")
sys.stdout.write(stats.text)
`;

type RedactResult = {
	text: string;
	bytesIn: number;
	bytesOut: number;
	redactionCount: number;
} | null;

function redactWithStats(text: string): RedactResult {
	let raw: string;
	try {
		raw = execFileSync("python3", ["-c", REDACT_HELPER], {
			input: text,
			encoding: "utf8",
			maxBuffer: 50 * 1024 * 1024,
		});
	} catch (e) {
		logFailure("redact", e);
		return null;
	}
	const newlineIdx = raw.indexOf("\n");
	if (newlineIdx < 0) {
		logFailure("redact_parse", new Error("missing header line"));
		return null;
	}
	const header = raw.slice(0, newlineIdx);
	const body = raw.slice(newlineIdx + 1);
	const parts = header.split("\t");
	if (parts.length !== 3) {
		logFailure("redact_parse", new Error(`bad header: ${header.slice(0, 80)}`));
		return null;
	}
	return {
		text: body,
		redactionCount: Number(parts[0]),
		bytesIn: Number(parts[1]),
		bytesOut: Number(parts[2]),
	};
}

function openDB(path: string): DatabaseSync {
	const db = new DatabaseSync(path, { allowExtension: true });
	db.enableLoadExtension(true);
	sqliteVec.load(db);
	db.enableLoadExtension(false);
	return db;
}

let extractor: Awaited<ReturnType<typeof pipeline>> | null = null;

async function getExtractor(): Promise<Awaited<ReturnType<typeof pipeline>>> {
	if (!extractor) {
		extractor = await pipeline("feature-extraction", EMBED_MODEL);
	}
	return extractor;
}

async function embed(text: string): Promise<Float32Array> {
	const ex = await getExtractor();
	const out = (await ex(text, {
		pooling: "mean",
		normalize: true,
	})) as unknown as {
		data: Float32Array;
	};
	return new Float32Array(out.data);
}

type DocFile = { path: string; name: string; body: string };

function readMemoryFiles(): DocFile[] {
	let files: string[];
	try {
		files = readdirSync(MEMORY_DIR).filter((f: string) => f.endsWith(".md"));
	} catch (e) {
		logFailure("readdir_memory", e);
		return [];
	}
	const out: DocFile[] = [];
	for (const f of files) {
		const path = join(MEMORY_DIR, f);
		try {
			out.push({ path, name: f, body: readFileSync(path, "utf8") });
		} catch (e) {
			logFailure(`read_file:${f}`, e);
		}
	}
	return out;
}

async function rebuildIndex(
	dbPath: string,
): Promise<{ indexed: number; skipped: number; anomalies: number }> {
	const db = openDB(dbPath);
	try {
		db.exec(`DROP TABLE IF EXISTS docs`);
		db.exec(`DROP TABLE IF EXISTS doc_vec`);
		db.exec(`
      CREATE TABLE docs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        path TEXT NOT NULL,
        body TEXT NOT NULL
      );
    `);
		db.exec(
			`CREATE VIRTUAL TABLE doc_vec USING vec0(embedding FLOAT[${DIM}]);`,
		);

		const insertDoc = db.prepare(
			`INSERT INTO docs (name, path, body) VALUES (?, ?, ?) RETURNING id`,
		);
		const insertVec = db.prepare(
			`INSERT INTO doc_vec (rowid, embedding) VALUES (?, ?)`,
		);

		const docs = readMemoryFiles();
		let indexed = 0;
		let skipped = 0;
		let anomalies = 0;
		for (const d of docs) {
			const stats = redactWithStats(d.body);
			if (stats === null) {
				skipped++;
				continue;
			}
			const clean = stats.text;
			if (!clean.trim()) {
				skipped++;
				continue;
			}
			if (stats.bytesIn > ANOMALY_BYTES_FLOOR && stats.bytesOut === 0) {
				// Defense-in-depth: redactor returned empty for non-trivial input.
				// Skip rather than embed a zero-signal vector.
				anomalies++;
				skipped++;
				continue;
			}
			try {
				const emb = await embed(clean.slice(0, 2000));
				const inserted = insertDoc.get(d.name, d.path, clean) as { id: number };
				insertVec.run(
					BigInt(inserted.id),
					new Uint8Array(emb.buffer, emb.byteOffset, emb.byteLength),
				);
				indexed++;
			} catch (e) {
				logFailure(`embed_insert:${d.name}`, e);
				skipped++;
			}
		}
		return { indexed, skipped, anomalies };
	} finally {
		db.close();
	}
}

async function main(): Promise<void> {
	const tStart = performance.now();
	const lock = acquireLock();
	if (!lock) {
		appendFileSync(
			LOG_FILE,
			JSON.stringify({
				ts: new Date().toISOString(),
				source: "memory-vec-reindex",
				stage: "lock_held",
				note: "another reindex in progress; this run is a no-op",
			}) + "\n",
			"utf8",
		);
		return;
	}
	try {
		// Atomic rebuild: write into tmp, rename to final on success.
		if (existsSync(DB_TMP)) {
			try {
				rmSync(DB_TMP, { force: true });
			} catch (e) {
				logFailure("tmp_cleanup_pre", e);
			}
		}

		let stats: { indexed: number; skipped: number; anomalies: number };
		try {
			stats = await rebuildIndex(DB_TMP);
		} catch (e) {
			logFailure("rebuild", e);
			try {
				rmSync(DB_TMP, { force: true });
			} catch (cleanErr) {
				logFailure("tmp_cleanup_post_fail", cleanErr);
			}
			// Touch existing DB so Stop hook does not retry forever on persistent failure.
			touchSentinel(DB_PATH);
			return;
		}

		try {
			renameSync(DB_TMP, DB_PATH);
		} catch (e) {
			logFailure("rename", e);
			touchSentinel(DB_PATH);
			return;
		}
		touchSentinel(DB_PATH);

		appendFileSync(
			LOG_FILE,
			JSON.stringify({
				ts: new Date().toISOString(),
				source: "memory-vec-reindex",
				stage: "complete",
				indexed: stats.indexed,
				skipped: stats.skipped,
				anomalies: stats.anomalies,
				elapsed_ms: Math.round(performance.now() - tStart),
			}) + "\n",
			"utf8",
		);
	} finally {
		releaseLock(lock);
	}
}

main().catch((e) => {
	logFailure("unhandled", e);
	touchSentinel(DB_PATH);
	process.exitCode = 1;
});
