# React Rules

## Hooks Rules

- NEVER call hooks inside conditions, loops, or nested functions
- Use `useRef` for values that should not trigger re-renders
- Extract complex logic into custom hooks with `use` prefix

## useEffect 禁止 — `useMountEffect` のみ許可

直接 `useEffect` を使わない。マウント時の外部同期が必要な場合のみ `useMountEffect` を使用する。

```typescript
// useMountEffect の定義
export function useMountEffect(effect: () => void | (() => void)) {
  useEffect(effect, []);
}
```

**代替パターン 5 つ:**

1. **派生状態はインラインで計算** — `useEffect(() => setX(f(y)), [y])` は `const x = f(y)` に置き換え
2. **データフェッチはライブラリ** — `useQuery` / `useSWR` 等を使い、effect 内の `fetch` + `setState` を排除
3. **イベントハンドラで直接実行** — ユーザー操作の結果は handler 内で処理。flag → effect → reset パターン禁止
4. **マウント時の外部同期は `useMountEffect`** — DOM 操作、サードパーティ連携、ブラウザ API サブスクリプション
5. **`key` でリセット** — props 変更時にコンポーネントを作り直したいなら `<Component key={id} />` を使う

```typescript
// ❌ BAD: effect で派生状態を同期
const [filtered, setFiltered] = useState([]);
useEffect(() => { setFiltered(items.filter(i => i.active)); }, [items]);

// ✅ GOOD: インライン計算
const filtered = items.filter(i => i.active);

// ❌ BAD: effect でフェッチ
useEffect(() => { fetchData(id).then(setData); }, [id]);

// ✅ GOOD: データフェッチライブラリ
const { data } = useQuery(['data', id], () => fetchData(id));

// ❌ BAD: effect で ID 変更を検知してリセット
useEffect(() => { loadVideo(videoId); }, [videoId]);

// ✅ GOOD: key でリマウント
<VideoPlayer key={videoId} videoId={videoId} />
```

**`useMountEffect` 内で最新の props/state が要る場合 — `useEffectEvent` (React 19.2+):**

購読・タイマー・外部連携のコールバックから最新値を読みたいだけなら、依存配列を増やさず `useEffectEvent` に非リアクティブなロジックを切り出す。制約 (`eslint-plugin-react-hooks` が強制する):

- effect の中からのみ呼ぶ。**render 中とイベントハンドラからは呼べない**
- 他のコンポーネントやフックに渡さない。effect 内で外部 API のコールバックとして直接渡すのは可
- **依存配列に入れない** (入れると lint が警告する)

```typescript
// ❌ BAD: 最新の theme が欲しいだけで再購読が走る
useEffect(() => { const c = createConnection(); c.on("open", () => notify(theme)); }, [theme]);

// ✅ GOOD: 再購読はさせず、最新値だけ読む
const onOpen = useEffectEvent(() => notify(theme));
useMountEffect(() => { const c = createConnection(); c.on("open", onOpen); return () => c.close(); });
```

**条件付きマウントは親で制御:**

```typescript
// ❌ BAD: effect 内でガード
useEffect(() => { if (!isLoading) playVideo(); }, [isLoading]);

// ✅ GOOD: 親で条件分岐してからマウント
{!isLoading && <VideoPlayer />}
// VideoPlayer 内で useMountEffect(() => playVideo())
```

## Composition Over Props Drilling

- Use children and render props to avoid passing data through many layers
- Prefer component composition: split into Container + Presentational
- Use context sparingly — only for truly global state (theme, auth, locale)
- For deep data sharing, consider co-locating state closer to consumers

## Server Components (Next.js App Router)

- Default to Server Components — add `"use client"` only when needed
- Keep `"use client"` boundaries as low as possible in the component tree
- Fetch data on the server — pass serializable props to client components
- Never import server-only code in client components

### Next.js 16 以降

- キャッシュは `use cache` ディレクティブで明示する (`next.config.ts` の `cacheComponents` フラグで有効化)。`unstable_cache` は置き換え対象
- `middleware.ts` は `proxy.ts` にリネームされた。ランタイムは nodejs 固定で、edge は使えない — 認証チェック等を edge 前提で書かない
- `cookies()` / `headers()` / `params` / `searchParams` は非同期。codemod (`npx @next/codemod@latest upgrade`) で大半は機械変換できる

## Memoization

- **React Compiler を既定で有効にする** — 1.0 stable (2025-10)。手動メモ化はコンパイラが外せなかった箇所だけに残す
  - React 19 未満 (17/18) でも使える。compiler config に `target` を指定し `react-compiler-runtime` を依存に追加する
  - lint は `eslint-plugin-react-hooks@latest` の recommended に統合済み。`eslint-plugin-react-compiler` を入れているなら削除する (コンパイラ未導入でも lint だけ先に上げてよい)
- Compiler なしの環境でのみ: `useMemo` / `useCallback` は default で付けない。計測してから、expensive computation・deps の参照安定・子の再レンダー抑止のいずれかに該当する場合だけ
- `React.memo()` for components that re-render with same props frequently

## Keys & Lists

- NEVER use array index as `key` for dynamic lists
- Use a stable, unique identifier from your data (e.g. `id`, `slug`)
- If no natural key exists, generate one at data creation time — not at render

```typescript
// BAD
items.map((item, i) => <Item key={i} {...item} />)

// GOOD
items.map((item) => <Item key={item.id} {...item} />)
```
