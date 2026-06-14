# memory-vec Vault Index Extension — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** memory-vec の意味検索インデックスを Obsidian Vault の記事フォルダ (`05-Literature`, `09-TechTrends`) にも拡張し、夜間バッチ／digest で集めた記事を Claude がオンデマンドで意味検索できるようにする(常時コンテキストは汚さない)。

**Architecture:** 既存の memory-vec は agent-memory (`memory/*.md`) のみを `index.db` (sqlite-vec, 384-dim) にフル再構築している。本変更は (1) 索引ソースを複数ルート化し各 doc に `source` 列を付与、(2) Stop hook の再索引トリガーを Vault 変更でも発火、(3) HANDOFF ヒントは `source="memory"` のみに絞って resume ヒントの希釈を防止、(4) オンデマンド検索 (`recall` / `query.ts`) は全ソース横断、とする。索引内容はコンテキストに載らず、パスヒント (top-5) と Read 展開のみ。

**Tech Stack:** TypeScript (node:sqlite + `--experimental-strip-types`), sqlite-vec (vec0 仮想テーブル), `@xenova/transformers` (Xenova/all-MiniLM-L6-v2), Python (Stop/SessionStart hooks)。テストは node 組込 `node:test` (TS は strip-types 実行) と既存 pytest。

---

## 前提となる既存インターフェース(実装者向けの事実)

実装前にこれらを理解すること。ソースは `~/.claude/skill-data/memory-vec/{reindex.ts,query.ts}` と `~/.claude/scripts/runtime/memory-vec-{stop,hint}-hook.py`。**これらは dotfiles の `.config/claude/` 配下のシンボリックリンク実体を編集する**(`~/.claude/` の実体は `dotfiles/.config/claude/`)。

1. **シンボリックリンク注意**: `~/.claude/skill-data/memory-vec/` の実体パスを最初に確認すること。`reindex.ts`/`query.ts` は `skill-data` 配下にあり、dotfiles 管理下か別管理かを `ls -l` + `git ls-files` で確認してから編集する。dotfiles 管理外なら本プランの「Files」パスを実体に読み替える。
2. **`docs` テーブル現状スキーマ**: `docs(id INTEGER PK AUTOINCREMENT, name TEXT, path TEXT, body TEXT)` + `doc_vec USING vec0(embedding FLOAT[384])`。`doc_vec.rowid = docs.id`。
3. **再構築は常にフルリビルド**: `reindex.ts` は `DROP TABLE` → `CREATE` → 全ファイル再投入。差分更新ではない。だから `source` 列追加は migration 不要(次回フルリビルドで新スキーマになる)。
4. **redaction 必須経路**: 各ファイル body は `redactWithStats()` (python `memory_redactor.redact_with_stats`) を通してから embed。`clean.trim() === ""` はスキップ、`bytesIn > 1024 && bytesOut === 0` は anomaly スキップ。Vault 記事も同経路を通す(無害)。
5. **embed 入力は先頭 2000 文字**: `embed(clean.slice(0, 2000))`。Vault 記事も同じ。
6. **Stop hook トリガー条件** (`memory-vec-stop-hook.py`): `max(mtime of MEMORY_DIR/*.md) > index.db mtime` なら background reindex を `subprocess.Popen` で発火。常に exit 0。
7. **SessionStart ヒント** (`memory-vec-hint-hook.py`): `HANDOFF.md` tail 1000 字をクエリに top-5 を引き、**パスのみ** stdout 出力 (`distance < 1.5` フィルタ)。file 本文は出さない。
8. **query.ts 出力**: stdout に JSON 配列 `[{path,name,distance}]`。vec0 KNN は `WHERE v.embedding MATCH ? AND v.k = ?` 構文。
9. **OBSIDIAN_VAULT_PATH**: 既定 `$HOME/Documents/Obsidian Vault`。Vault 記事フォルダは `05-Literature/` (83 ノート) と `09-TechTrends/` (日次ダンプ)。
10. **embed モデルは既にディスクキャッシュ済**(夜間 reindex 実績あり)ので、テストで実 embedding を呼んでよい(初回のみ HF DL の可能性)。

---

## File Structure

**修正(memory-vec コア):**
- `<skill-data>/memory-vec/reindex.ts` — 索引ソース複数化 + `source` 列追加。責務: 全ソースルートから md 収集 → redact → embed → `index.db` フルリビルド。
- `<skill-data>/memory-vec/query.ts` — `source` を SELECT に追加して返す + 任意 `--source <name>` フィルタ(over-fetch + filter)。責務: クエリ embed → KNN → JSON 出力。

**修正(hooks, dotfiles 管理下):**
- `.config/claude/scripts/runtime/memory-vec-stop-hook.py` — 再索引トリガーの mtime 走査に Vault 記事フォルダを追加。責務: 変更検知して reindex 発火。
- `.config/claude/scripts/runtime/memory-vec-hint-hook.py` — HANDOFF ヒントを `--source memory` に限定(希釈防止)。責務: resume ヒント生成。

**新規(テスト):**
- `<skill-data>/memory-vec/reindex.test.ts` — `readSourceFiles()` の複数ルート収集 + source タグのユニットテスト。
- `<skill-data>/memory-vec/query.test.ts` — 小さな fixture index に対する source フィルタ動作の統合テスト。
- `.config/claude/scripts/tests/test_memory_vec_trigger.py` — stop-hook の mtime 走査が Vault フォルダを含むことの検証。

**責務境界:** reindex.ts = 索引構築(複数ソース)、query.ts = 検索(source 返却 + 任意フィルタ)、stop-hook = 発火トリガー、hint-hook = resume ヒント(memory 限定)。索引内容は一切コンテキストに載せない(パスヒント + Read 展開のみ)— この不変条件を壊さないこと。

---

## Task 1: 実体パスとビルド前提の確認

**Files:**
- 確認のみ(編集なし)

- [ ] **Step 1: skill-data の実体と git 管理状況を確認**

Run:
```bash
ls -l ~/.claude/skill-data/memory-vec/reindex.ts
cd ~/dotfiles && git ls-files --error-unmatch .config/claude/skill-data/memory-vec/reindex.ts 2>&1 || echo "NOT_IN_DOTFILES_GIT"
```
Expected: 実体パスが判明する。dotfiles 管理下なら `.config/claude/skill-data/...` が返る。`NOT_IN_DOTFILES_GIT` の場合は本プランの `<skill-data>` を実体絶対パスに読み替え、変更を別途バックアップ管理する(コミット経路をユーザーに確認)。

- [ ] **Step 2: node + 依存が動くことを確認**

Run:
```bash
cd ~/.claude/skill-data/memory-vec && node --experimental-strip-types --no-warnings -e "import('sqlite-vec').then(()=>console.log('sqlite-vec OK'))"
```
Expected: `sqlite-vec OK`。失敗時は `pnpm install` を当該ディレクトリで実行してから再確認。

- [ ] **Step 3: 現状 index.db のスキーマを記録(リグレッション基準)**

Run:
```bash
node --experimental-strip-types --no-warnings -e "const {DatabaseSync}=require('node:sqlite'); const db=new DatabaseSync(process.env.HOME+'/.claude/skill-data/memory-vec/index.db'); console.log(db.prepare('SELECT count(*) c FROM docs').get());"
```
Expected: 現在の doc 件数(~78)。この数字を記録。変更後 Vault 込みで増えることの確認に使う。

---

## Task 2: reindex.ts — 索引ソースの複数ルート化 + source 列

**Files:**
- Modify: `<skill-data>/memory-vec/reindex.ts`
- Test: `<skill-data>/memory-vec/reindex.test.ts`

- [ ] **Step 1: failing test を書く(readSourceFiles の複数ルート収集 + source タグ)**

`reindex.ts` の `readMemoryFiles()` を `readSourceFiles(sources)` にリファクタした後の挙動をテストする。まずテストを書く:

```typescript
// reindex.test.ts
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
```

- [ ] **Step 2: test を実行して fail することを確認**

Run: `cd ~/.claude/skill-data/memory-vec && node --experimental-strip-types --test reindex.test.ts`
Expected: FAIL(`readSourceFiles` が export されていない / 未定義)。

- [ ] **Step 3: reindex.ts に source 設定と readSourceFiles を実装**

`reindex.ts` の定数部 (L44-58 付近) に Vault ソースを追加:

```typescript
const HOME = homedir();
const MEMORY_DIR = join(
  HOME,
  ".claude/projects/-Users-takeuchishougo-dotfiles/memory",
);
const VAULT_PATH = process.env.OBSIDIAN_VAULT_PATH
  ? process.env.OBSIDIAN_VAULT_PATH
  : join(HOME, "Documents/Obsidian Vault");

type SourceRoot = { root: string; source: string };

const SOURCES: SourceRoot[] = [
  { root: MEMORY_DIR, source: "memory" },
  { root: join(VAULT_PATH, "05-Literature"), source: "vault" },
  { root: join(VAULT_PATH, "09-TechTrends"), source: "vault" },
];
```

`DocFile` 型に `source` を追加し、`readMemoryFiles()` を `readSourceFiles()` に置換(export する):

```typescript
type DocFile = { path: string; name: string; body: string; source: string };

export function readSourceFiles(sources: SourceRoot[]): DocFile[] {
  const out: DocFile[] = [];
  for (const { root, source } of sources) {
    let files: string[];
    try {
      files = readdirSync(root).filter((f: string) => f.endsWith(".md"));
    } catch (e) {
      logFailure(`readdir:${source}:${root}`, e);
      continue;
    }
    for (const f of files) {
      const path = join(root, f);
      try {
        out.push({ path, name: f, body: readFileSync(path, "utf8"), source });
      } catch (e) {
        logFailure(`read_file:${f}`, e);
      }
    }
  }
  return out;
}
```

- [ ] **Step 4: test を実行して pass することを確認**

Run: `cd ~/.claude/skill-data/memory-vec && node --experimental-strip-types --test reindex.test.ts`
Expected: PASS(2 tests)。

- [ ] **Step 5: docs テーブルに source 列 + 投入経路を更新**

`rebuildIndex()` 内 (L259-310) を更新。CREATE TABLE に `source` 追加:

```typescript
db.exec(`
  CREATE TABLE docs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    path TEXT NOT NULL,
    body TEXT NOT NULL,
    source TEXT NOT NULL
  );
`);
```

insertDoc を更新:

```typescript
const insertDoc = db.prepare(
  `INSERT INTO docs (name, path, body, source) VALUES (?, ?, ?, ?) RETURNING id`,
);
```

`readMemoryFiles()` 呼び出しを `readSourceFiles(SOURCES)` に置換し、insert に source を渡す:

```typescript
const docs = readSourceFiles(SOURCES);
// ... ループ内 ...
const inserted = insertDoc.get(d.name, d.path, clean, d.source) as { id: number };
```

- [ ] **Step 6: 手動フルリビルドして Vault 込みで件数が増えることを確認**

Run:
```bash
cd ~/.claude/skill-data/memory-vec && node --experimental-strip-types --no-warnings reindex.ts && node --experimental-strip-types --no-warnings -e "const {DatabaseSync}=require('node:sqlite'); const db=new DatabaseSync(process.env.HOME+'/.claude/skill-data/memory-vec/index.db'); console.log(db.prepare('SELECT source, count(*) c FROM docs GROUP BY source').all());"
```
Expected: `[{source:'memory', c:~78}, {source:'vault', c:~89}]`。Task 1 Step 3 の数字より増えている。

- [ ] **Step 7: コミット**

```bash
cd ~/dotfiles && git add .config/claude/skill-data/memory-vec/reindex.ts .config/claude/skill-data/memory-vec/reindex.test.ts
git commit -m "feat(memory-vec): index Vault article folders with source column"
```
(Task 1 Step 1 で dotfiles 管理外と判明した場合はコミット経路をユーザーに確認してから。)

---

## Task 3: query.ts — source 返却 + 任意 source フィルタ

**Files:**
- Modify: `<skill-data>/memory-vec/query.ts`
- Test: `<skill-data>/memory-vec/query.test.ts`

**設計判断(正直な注記):** vec0 の KNN (`MATCH ... AND k = ?`) はベクトル距離で top-k を返すため、JOIN 後の `source` で WHERE 絞りすると k 未満になりうる。よって **over-fetch (k=20) → JS 側で source フィルタ → 先頭 5 件** とする。Step 3 で実 API 挙動を確認し、もし vec0 が `WHERE d.source = ?` の事前絞りに対応していれば(バージョン依存)そちらに切替可。

- [ ] **Step 1: failing test を書く(source フィルタ)**

```typescript
// query.test.ts
import { test } from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { queryIndex } from "./query.ts";

// 小さな fixture index を作るヘルパは reindex の openDB/embed を再利用。
// ここでは queryIndex(dbPath, queryText, {source?}) の契約をテストする。
test("queryIndex returns source field and filters by source when given", async () => {
  // fixture: メモリ1件 + vault1件 を投入した tmp index を構築
  const base = mkdtempSync(join(tmpdir(), "mvq-"));
  const dbPath = join(base, "index.db");
  await buildFixtureIndex(dbPath, [
    { name: "m.md", path: "/m.md", body: "go concurrency goroutine", source: "memory" },
    { name: "v.md", path: "/v.md", body: "go concurrency goroutine", source: "vault" },
  ]);

  const all = await queryIndex(dbPath, "go concurrency", {});
  assert.ok(all.every((r) => typeof r.source === "string"));
  assert.ok(all.some((r) => r.source === "vault"));

  const memOnly = await queryIndex(dbPath, "go concurrency", { source: "memory" });
  assert.ok(memOnly.every((r) => r.source === "memory"));
  rmSync(base, { recursive: true, force: true });
});
```

(`buildFixtureIndex` は query.test.ts 内に定義 — reindex.ts の `openDB` を import し、docs/doc_vec を CREATE して 2 行 embed 投入する小ヘルパ。embed は query.ts の `embed` を export して再利用する。)

- [ ] **Step 2: test を実行して fail することを確認**

Run: `cd ~/.claude/skill-data/memory-vec && node --experimental-strip-types --test query.test.ts`
Expected: FAIL(`queryIndex` / `embed` が未 export)。

- [ ] **Step 3: query.ts をリファクタ — queryIndex を export し source 対応**

`main()` のロジックを `queryIndex(dbPath, query, opts)` に抽出し export。`embed` と `openDB` も export(テスト/フィクスチャ用)。SELECT に `d.source` を追加し、over-fetch + filter:

```typescript
export async function embed(text: string): Promise<Float32Array> { /* 既存実装のまま */ }
export function openDB(path: string): DatabaseSync { /* 既存実装のまま */ }

const OVERFETCH_K = 20;

export type QueryRow = { path: string; name: string; distance: number; source: string };

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
```

`main()` は CLI 引数 (`process.argv[2]` = query, `--source <name>` 任意) をパースして `queryIndex` を呼び JSON 出力するだけに:

```typescript
async function main(): Promise<void> {
  const query = process.argv[2];
  if (!query || !query.trim()) process.exit(2);
  const srcIdx = process.argv.indexOf("--source");
  const source = srcIdx >= 0 ? process.argv[srcIdx + 1] : undefined;
  const rows = await queryIndex(DB_PATH, query, { source });
  process.stdout.write(JSON.stringify(rows));
}
```

- [ ] **Step 4: test を実行して pass することを確認**

Run: `cd ~/.claude/skill-data/memory-vec && node --experimental-strip-types --test query.test.ts`
Expected: PASS。

- [ ] **Step 5: CLI 後方互換を確認(既存 hint hook が壊れない)**

Run:
```bash
cd ~/.claude/skill-data/memory-vec && node --experimental-strip-types --no-warnings query.ts "test query" | head -c 400
```
Expected: JSON 配列が出る。各要素に `source` フィールドが増えている(既存 consumer は path/name/distance を読むので後方互換)。

- [ ] **Step 6: source フィルタの CLI 動作確認**

Run:
```bash
cd ~/.claude/skill-data/memory-vec && node --experimental-strip-types --no-warnings query.ts "test query" --source memory | node -e "let s='';process.stdin.on('data',d=>s+=d).on('end',()=>{const a=JSON.parse(s);console.log('all memory:', a.every(r=>r.source==='memory'), 'n=',a.length)})"
```
Expected: `all memory: true n=<=5`。

- [ ] **Step 7: コミット**

```bash
cd ~/dotfiles && git add .config/claude/skill-data/memory-vec/query.ts .config/claude/skill-data/memory-vec/query.test.ts
git commit -m "feat(memory-vec): return source field and support --source filter in query"
```

---

## Task 4: hint-hook — HANDOFF ヒントを memory 限定にして希釈防止

**Files:**
- Modify: `.config/claude/scripts/runtime/memory-vec-hint-hook.py:139-158` (`_run_query`)

- [ ] **Step 1: _run_query が --source memory を渡すよう変更**

`_run_query` の subprocess 引数 (L143-151) に `--source memory` を追加:

```python
        result = subprocess.run(
            [
                node_bin,
                "--experimental-strip-types",
                "--no-warnings",
                str(QUERY_SCRIPT),
                query,
                "--source",
                "memory",
            ],
            capture_output=True,
            text=True,
            timeout=QUERY_TIMEOUT_SEC,
            check=False,
        )
```

理由(コメントとして付記): HANDOFF resume ヒントは agent-memory のみを対象とし、Vault 記事 (vault source) でヒント枠 (top-5) を希釈しない。Vault はオンデマンド recall で検索する。

- [ ] **Step 2: 手動でヒント出力を確認(memory パスのみ)**

Run:
```bash
cd /tmp && printf "go concurrency design decision" > HANDOFF.md && echo '{"cwd":"/tmp"}' | python3 ~/.claude/scripts/runtime/memory-vec-hint-hook.py; rm -f /tmp/HANDOFF.md
```
Expected: `[Memory Hint]` ブロックが出る場合、列挙パスが全て agent-memory 配下(`memory/*.md`)で、`05-Literature`/`09-TechTrends` を含まない。

- [ ] **Step 3: validate-configs + コミット**

Run: `cd ~/dotfiles && task validate-configs`
Expected: PASS。
```bash
git add .config/claude/scripts/runtime/memory-vec-hint-hook.py
git commit -m "feat(memory-vec): restrict HANDOFF hint to memory source (avoid vault dilution)"
```

---

## Task 5: stop-hook — Vault 変更でも再索引を発火

**Files:**
- Modify: `.config/claude/scripts/runtime/memory-vec-stop-hook.py:19-21,82-104`
- Test: `.config/claude/scripts/tests/test_memory_vec_trigger.py`

- [ ] **Step 1: failing test を書く(走査対象に Vault フォルダが含まれる)**

```python
# test_memory_vec_trigger.py
import importlib.util
from pathlib import Path

SPEC = Path.home() / ".claude/scripts/runtime/memory-vec-stop-hook.py"

def _load():
    spec = importlib.util.spec_from_file_location("mv_stop", SPEC)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def test_scan_dirs_includes_vault_article_folders(monkeypatch, tmp_path):
    monkeypatch.setenv("OBSIDIAN_VAULT_PATH", str(tmp_path / "vault"))
    mod = _load()
    dirs = mod.scan_dirs()
    names = [Path(d).name for d in dirs]
    assert "05-Literature" in names
    assert "09-TechTrends" in names
    assert any("memory" in str(d) for d in dirs)
```

- [ ] **Step 2: test を実行して fail することを確認**

Run: `cd ~/dotfiles && python3 -m pytest .config/claude/scripts/tests/test_memory_vec_trigger.py -v`
Expected: FAIL(`scan_dirs` 未定義)。

- [ ] **Step 3: stop-hook に scan_dirs を実装し mtime 走査を複数ディレクトリ化**

定数部 (L19-21) に Vault を追加:

```python
import os

MEMORY_DIR = (
    Path.home() / ".claude" / "projects" / "-Users-takeuchishougo-dotfiles" / "memory"
)


def _vault_path() -> Path:
    env = os.environ.get("OBSIDIAN_VAULT_PATH")
    return Path(env) if env else Path.home() / "Documents" / "Obsidian Vault"


def scan_dirs() -> list[Path]:
    vault = _vault_path()
    return [MEMORY_DIR, vault / "05-Literature", vault / "09-TechTrends"]
```

`main()` の mtime 走査 (L82-91) を複数ディレクトリ対応に置換:

```python
    try:
        md_files: list[Path] = []
        for d in scan_dirs():
            if d.is_dir():
                md_files.extend(d.glob("*.md"))
        if not md_files:
            return 0

        latest_md_mtime = max(f.stat().st_mtime for f in md_files)
        db_mtime = INDEX_DB.stat().st_mtime if INDEX_DB.is_file() else 0.0

        if latest_md_mtime <= db_mtime:
            return 0

        subprocess.Popen(
            [
                node_bin,
                "--experimental-strip-types",
                "--no-warnings",
                str(REINDEX_SCRIPT),
            ],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except (OSError, ValueError) as exc:
        _log("dispatch", exc)
```

L74 の `if not MEMORY_DIR.is_dir()` ガードは `if not REINDEX_SCRIPT.is_file()` のみに緩める(Vault だけ存在する環境でも動くように):

```python
    if not REINDEX_SCRIPT.is_file():
        return 0
```

- [ ] **Step 4: test を実行して pass することを確認**

Run: `cd ~/dotfiles && python3 -m pytest .config/claude/scripts/tests/test_memory_vec_trigger.py -v`
Expected: PASS。

- [ ] **Step 5: 既存挙動の非回帰確認(memory のみ変更時も発火する)**

Run:
```bash
cd ~/dotfiles && python3 -c "
import importlib.util, pathlib
spec=importlib.util.spec_from_file_location('m', pathlib.Path.home()/'.claude/scripts/runtime/memory-vec-stop-hook.py')
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
print('scan_dirs:', [str(d) for d in m.scan_dirs()])
"
```
Expected: 3 ディレクトリ(memory + 05-Literature + 09-TechTrends)が出る。

- [ ] **Step 6: validate-configs + コミット**

Run: `cd ~/dotfiles && task validate-configs`
Expected: PASS。
```bash
git add .config/claude/scripts/runtime/memory-vec-stop-hook.py .config/claude/scripts/tests/test_memory_vec_trigger.py
git commit -m "feat(memory-vec): trigger reindex on Vault article changes"
```

---

## Task 6: 統合検証(E2E)

**Files:**
- 検証のみ

- [ ] **Step 1: フルリビルド → Vault 記事の意味検索がヒットすることを確認**

Run:
```bash
cd ~/.claude/skill-data/memory-vec && node --experimental-strip-types --no-warnings reindex.ts
# Vault にある既知トピック(例: servant engineering / nix mise)で検索
node --experimental-strip-types --no-warnings query.ts "servant engineering review speed" | python3 -m json.tool
```
Expected: 結果に `05-Literature/lit-nrslib-servant-engineering.md` 等の vault パスが `source:"vault"` で出る。

- [ ] **Step 2: HANDOFF ヒントが memory に限定されることを再確認(Task 4 Step 2 と同じ)**

Run:
```bash
cd /tmp && printf "servant engineering review speed" > HANDOFF.md && echo '{"cwd":"/tmp"}' | python3 ~/.claude/scripts/runtime/memory-vec-hint-hook.py; rm -f /tmp/HANDOFF.md
```
Expected: ヒントに vault パスが出ない(memory のみ)。Vault は Step 1 のオンデマンド検索でのみ出る = 設計通り。

- [ ] **Step 3: 全テストスイート + validate**

Run:
```bash
cd ~/dotfiles && task validate && python3 -m pytest .config/claude/scripts/tests/test_memory_vec_trigger.py -q
cd ~/.claude/skill-data/memory-vec && node --experimental-strip-types --test reindex.test.ts query.test.ts
```
Expected: 全 PASS。

- [ ] **Step 4: index.db サイズが想定内(~5M, 汚染ではない)であることを確認**

Run: `du -h ~/.claude/skill-data/memory-vec/index.db`
Expected: ~5M 前後(memory 78 + vault 89 ≈ 167 doc)。これはディスクであってコンテキストではない(不変条件の確認)。

---

## Scope (In/Out)

**In:**
- 05-Literature + 09-TechTrends を memory-vec に索引
- source 列 + source フィルタ
- HANDOFF ヒントは memory 限定(希釈防止)
- Stop hook が Vault 変更で再索引

**Out(別タスク):**
- P1 ソース拡充 / P2 ハーネス absorb→PR(Phase 2 マージ後)
- Vault 全フォルダ索引(記事2フォルダにスコープ)
- 差分(incremental)索引(現状フルリビルドのまま — 167 doc 規模では不要、YAGNI)
- `recall` skill 側の UI 変更(query.ts が source を返すので必要なら別途)

## Success Criteria

- `query.ts "<topic>"` が Vault 記事を `source:"vault"` でヒットさせる
- HANDOFF ヒントに vault パスが混じらない(コンテキスト非汚染 + 希釈なし)
- 既存の agent-memory 索引・hint・recall が非回帰
- index.db はディスク増のみ(コンテキストトークン増ゼロ)

## Open Questions

- Task 1 Step 1 で skill-data が dotfiles git 管理外と判明した場合のコミット/同期経路(ユーザー確認)
- `recall` skill が query.ts の新 `source` フィールドをどう表示するか(表示改善は任意・別タスク)
