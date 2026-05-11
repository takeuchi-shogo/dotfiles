# Playwright Test on GitHub Actions

`/playwright-test` skill の GitHub Actions セクションを切り出した詳細レシピ集。
SKILL.md からは sub-section 一覧のみ参照され、ここで完全な YAML / TS スニペットを保持する。

---

## GitHub Actions

### Linux Fonts (Required on CI)

Ubuntu/Debian does not ship with Japanese/CJK fonts by default. This causes mojibake and layout breakage in screenshots:

```yaml
      - name: Install fonts
        run: |
          sudo apt-get update
          sudo apt-get install -y fonts-noto-cjk fonts-noto-color-emoji
```

The `--with-deps` option makes Playwright install the required system dependencies, but fonts are not included.

### Basic (without shard)

```yaml
name: E2E Tests
on: [push, pull_request]

jobs:
  e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 24 }
      - run: npm ci
      - run: npx playwright install chromium --with-deps
      - run: sudo apt-get install -y fonts-noto-cjk fonts-noto-color-emoji
      - run: npx playwright test
      - uses: actions/upload-artifact@v4
        if: ${{ !cancelled() }}
        with:
          name: playwright-report
          path: playwright-report/
          retention-days: 14
```

### Shard Execution (Parallel Splitting)

Split tests across multiple jobs to speed them up:

```yaml
name: E2E Tests (Sharded)
on: [push, pull_request]

jobs:
  e2e:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        shard: [1/4, 2/4, 3/4, 4/4]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 24 }
      - run: npm ci
      - run: npx playwright install chromium --with-deps
      - run: npx playwright test --shard=${{ matrix.shard }}
      - uses: actions/upload-artifact@v4
        if: ${{ !cancelled() }}
        with:
          name: blob-report-${{ strategy.job-index }}
          path: blob-report/
          retention-days: 1

  merge-reports:
    if: ${{ !cancelled() }}
    needs: e2e
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 24 }
      - run: npm ci
      - uses: actions/download-artifact@v4
        with:
          path: all-blob-reports
          pattern: blob-report-*
          merge-multiple: true
      - run: npx playwright merge-reports --reporter html ./all-blob-reports
      - uses: actions/upload-artifact@v4
        with:
          name: playwright-report
          path: playwright-report/
          retention-days: 14
```

Add the blob reporter to the config for sharding:

```ts
reporter: process.env.CI
  ? [['blob'], ['github']]    // For shards: emit blob
  : [['html']],
```

### Shard x Browser Matrix (Multiple Browsers in Parallel)

To run multiple browsers x multiple shards together, use two `matrix` axes:

```yaml
jobs:
  e2e:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        browser: [chromium, firefox, webkit]
        shard: [1/4, 2/4, 3/4, 4/4]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 24 }
      - run: npm ci
      - run: npx playwright install ${{ matrix.browser }} --with-deps
      - run: sudo apt-get install -y fonts-noto-cjk fonts-noto-color-emoji
      - run: npx playwright test --project=${{ matrix.browser }} --shard=${{ matrix.shard }}
      - uses: actions/upload-artifact@v4
        if: ${{ !cancelled() }}
        with:
          name: blob-${{ matrix.browser }}-${{ strategy.job-index }}
          path: blob-report/
          retention-days: 1
```

The merge job consolidates all blobs into a single HTML. Since the artifact name varies per browser x shard (`blob-chromium-0` / `blob-firefox-1` ...), use `blob-*` as the pattern:

```yaml
  merge-reports:
    if: ${{ !cancelled() }}
    needs: e2e
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 24 }
      - run: npm ci
      - uses: actions/download-artifact@v4
        with:
          path: all-blob-reports
          pattern: blob-*             # Collect across browsers
          merge-multiple: true
      - run: npx playwright merge-reports --reporter html ./all-blob-reports
      - uses: actions/upload-artifact@v4
        with:
          name: playwright-report
          path: playwright-report/
          retention-days: 14
```

Job count becomes `browsers x shards` (3 x 4 = 12 jobs), so watch the combinatorial blow-up. `fail-fast: false` keeps other jobs running when one fails. `workers: 1` controls parallelism **within a shard** (shards are already parallel, so 1 is fine on CI; use `undefined` for auto on local dev).

### Retry Strategy

```ts
// playwright.config.ts
export default defineConfig({
  retries: process.env.CI ? 2 : 0,  // Up to 2 retries on CI

  use: {
    trace: 'on-first-retry',         // Capture trace on retry
    screenshot: 'only-on-failure',
    video: 'on-first-retry',
  },
});
```

Per-test retries:

```ts
// Change retry count for a specific test only
test('flaky external API test', async ({ page }) => {
  test.info().annotations.push({ type: 'retry', description: 'External dependency' });
  // ...
});

// Per describe
test.describe('payment flow', () => {
  test.describe.configure({ retries: 3 });
  // ...
});
```

### Choosing Trace / Screenshot / Video

| Setting | When captured | Purpose / Size |
|---|---|---|
| `'on'` | Every test | Debug only. Not recommended on CI (artifacts balloon) |
| `'on-first-retry'` | Only on retry | **Recommended CI default**. Sufficient for flaky investigation, minimal size |
| `'retain-on-failure'` | Kept on failure | When you want to catch a failure on the very first run. Useful when retries are disabled |
| `'off'` | Never captured | Save artifact space on large suites |

Selection criteria: **if you set retries >= 1, use `on-first-retry`** (initial fail -> trace on retry, half the size). **Without retries, or when you want to inspect a single failure immediately, use `retain-on-failure`**. When the requirement is phrased as "failure only," it usually means `retain-on-failure`.

### Browser-Conditional Tests

Skipping or handling differences per browser:

```ts
import { test } from '@playwright/test';

// Skip one test based on browser condition
test('webkit only feature', async ({ page, browserName }) => {
  test.skip(browserName !== 'webkit', 'Safari-specific behavior');
  // ...
});

// Skip a describe block
test.describe('chromium-only suite', () => {
  test.skip(({ browserName }) => browserName !== 'chromium', 'Uses CDP');
  test('uses cdp api', async ({ page }) => { /* ... */ });
});

// Change retry / mode per describe
test.describe('payment flow', () => {
  test.describe.configure({ retries: 3, mode: 'serial' });
  test('step 1', async ({ page }) => { /* ... */ });
  test('step 2', async ({ page }) => { /* inherits state from step 1 */ });
});
```

`browserName` takes one of three values: `chromium` / `firefox` / `webkit`. Combining with tag-based CLI filtering (`--grep @chromium-only`) gives more flexibility in CI configuration.

### Flaky Detection Workflow

To detect flaky tests on CI and post comments / aggregate stats on PRs, add the JSON reporter:

```ts
reporter: process.env.CI
  ? [['blob'], ['github'], ['json', { outputFile: 'test-results/results.json' }]]
  : [['html']],
```

`results.json` contains each test's `status` / `retries` / `duration`. Extract downstream:

```bash
# retry > 0 and final pass = flaky candidate
jq '.suites[].specs[] | select(.tests[].results | length > 1 and .[-1].status == "passed")' \
  test-results/results.json
```

The usual pattern is to upload as an artifact on GitHub Actions and aggregate in a separate job -> track trends over the past N runs. With `@playwright/test` 1.40+, built-in support like `expect.configure({ flaky: true })` is also available.
