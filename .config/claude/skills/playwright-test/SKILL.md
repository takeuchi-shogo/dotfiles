---
name: playwright-test
description: Best practices and reference for Playwright Test (E2E). Covers how to write tests, avoiding fixed waits, network triggers, DnD, shard/retry setup on GitHub Actions, and more. Use when writing, reviewing, or configuring CI for Playwright tests.
origin: external
---

# Playwright Test

## Configuration Template

```ts
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,       // Forbid .only on CI
  retries: process.env.CI ? 2 : 0,    // Retry only on CI
  workers: process.env.CI ? 1 : undefined,
  reporter: process.env.CI
    ? [['html'], ['github']]           // CI: HTML + GitHub annotations
    : [['html']],
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',          // Record trace only on retry
    screenshot: 'only-on-failure',
    video: 'on-first-retry',
  },
  projects: [
    { name: 'setup', testMatch: /.*\.setup\.ts/ },
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'], storageState: 'playwright/.auth/user.json' },
      dependencies: ['setup'],
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'], storageState: 'playwright/.auth/user.json' },
      dependencies: ['setup'],
    },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
  },
});
```

## GitHub Actions

CI 上で Playwright Test を実行するレシピ集 (Linux fonts / Basic / Shard / Browser Matrix /
Retry / Trace 選択 / Browser-conditional / Flaky detection)。

完全な YAML / TS スニペット: [`references/github-actions.md`](references/github-actions.md)


## Rule: Do Not Use Fixed Waits

Playwright automatically waits until an element is actionable. `waitForTimeout()` is forbidden.

```ts
// BAD
await page.waitForTimeout(3000);
await page.click('#submit');

// GOOD: automatic waiting
await page.getByRole('button', { name: 'Submit' }).click();

// GOOD: web-first assertion (auto-retries)
await expect(page.getByText('Success')).toBeVisible();

// BAD: no retry
expect(await page.getByText('Success').isVisible()).toBe(true);
```

**One-shot read APIs do not auto-retry**:

| Form | Behavior |
|---|---|
| `expect(locator).toBeVisible()` / `toHaveText(...)` etc. | **Auto-retry** (default 5s). Use these |
| `await locator.isVisible()` / `innerText()` / `count()` / `textContent()` | **One-shot read, no retry**. A hotbed for flaky tests |

If a test is flaky, there's a good chance you can replace a one-shot API with a web-first assertion:

```ts
// BAD
const n = await page.locator('.row').count();
expect(n).toBeGreaterThan(0);

// GOOD
await expect(page.locator('.row')).not.toHaveCount(0);
```

Cases where explicit waiting is necessary:

```ts
await page.waitForURL('**/dashboard');          // After navigation
await page.waitForLoadState('networkidle');      // Heavy initial load
await page.waitForResponse('**/api/data');       // Wait for API response
```

## Network Triggers

Set up the Promise **before** the action:

```ts
const responsePromise = page.waitForResponse('**/api/users');
await page.getByRole('button', { name: 'Save' }).click();
const response = await responsePromise;
expect(response.status()).toBe(200);

// Conditional matching
const responsePromise = page.waitForResponse(
  resp => resp.url().includes('/api/users') && resp.request().method() === 'POST'
);
```

**Pitfall: `waitForResponse` hanging forever**: If the target API is never called (an SPA with all data in the initial bundle, skipped on cache hit, etc.), it blocks until timeout. **Fallback priority**:

1. First decide whether `waitForResponse` is necessary (needed when an API call is the definitive timing of a side effect)
2. If the API is not called, a **web-first assertion alone** is enough (`await expect(page.getByTestId('result')).toBeVisible()`)
3. To cap the timeout, pass `{ timeout: 5_000 }`
4. To count arbitrary responses, use `page.on('response', ...)` as a listener (event aggregation rather than waitFor)

### API Mocking

Register `page.route()` **before** `page.goto()`:

```ts
await page.route('**/api/items', route => route.fulfill({
  status: 200,
  contentType: 'application/json',
  body: JSON.stringify({ items: [{ id: 1, name: 'Test' }] }),
}));

// Modify the response
await page.route('**/api/data', async route => {
  const response = await route.fetch();
  const json = await response.json();
  json.debug = true;
  await route.fulfill({ response, json });
});

// Block resources (speed up)
await page.route('**/*.{png,jpg,jpeg}', route => route.abort());
```

### Network Record/Replay via HAR

Record real API responses and replay them verbatim during tests:

```ts
// Record: generate a HAR file during test execution
test('record HAR', async ({ page }) => {
  await page.routeFromHAR('tests/fixtures/api.har', {
    url: '**/api/**',
    update: true,  // true = record mode, false = replay mode
  });
  await page.goto('/');
  // ...interactions save API responses to the HAR
});

// Replay: return responses from the recorded HAR (no network needed)
test('replay from HAR', async ({ page }) => {
  await page.routeFromHAR('tests/fixtures/api.har', {
    url: '**/api/**',
    update: false,  // replay mode
  });
  await page.goto('/');
  await expect(page.getByText('data from API')).toBeVisible();
});
```

Record a HAR from the CLI:

```bash
npx playwright open --save-har=tests/fixtures/api.har https://example.com
```

### Request / Response Assertions

```ts
// Validate the request body
const requestPromise = page.waitForRequest('**/api/submit');
await page.getByRole('button', { name: 'Submit' }).click();
const request = await requestPromise;
expect(request.method()).toBe('POST');
expect(JSON.parse(request.postData()!)).toEqual({ name: 'test' });

// Validate the response body
const responsePromise = page.waitForResponse('**/api/submit');
await page.getByRole('button', { name: 'Submit' }).click();
const response = await responsePromise;
const body = await response.json();
expect(body.id).toBeDefined();
```

### Context-Level Routing

To apply a common mock to every page, use `context.route()`:

```ts
test('context-level mock', async ({ context, page }) => {
  // Applies to every page in the context
  await context.route('**/api/config', route => route.fulfill({
    status: 200,
    json: { featureFlag: true },
  }));
  await page.goto('/');
  const popup = await page.waitForEvent('popup');  // Also applies to new tabs
  await expect(popup.getByText('Feature enabled')).toBeVisible();
});
```

## Drag and Drop

### Simple Case

```ts
await page.locator('#source').dragTo(page.locator('#target'));
```

### DnD Libraries (react-dnd, dnd-kit, SortableJS)

Pointer-event-based libraries often don't work with `dragTo`:

```ts
async function dragAndDrop(page: Page, source: Locator, target: Locator) {
  const srcBox = (await source.boundingBox())!;
  const tgtBox = (await target.boundingBox())!;

  await page.mouse.move(srcBox.x + srcBox.width / 2, srcBox.y + srcBox.height / 2);
  await page.mouse.down();
  await page.mouse.move(tgtBox.x + tgtBox.width / 2, tgtBox.y + tgtBox.height / 2, { steps: 10 });
  await page.mouse.up();
}
```

- `{ steps: 10 }` generates intermediate `pointermove`/`dragover` events
- Libraries that use `DataTransfer` may require synthesized events via `page.evaluate()`
- Assert the final state (element order/position), not the animation

## Locators

Priority order (higher is preferred):

```ts
page.getByRole('button', { name: 'Submit' });  // 1. Role-based
page.getByLabel('Email');                        // 2. Label
page.getByText('Welcome');                       // 2. Text
page.getByTestId('nav-menu');                    // 3. Test ID
page.locator('button.btn-primary');              // 4. CSS (avoid)
```

Chains and filters:

```ts
const product = page.getByRole('listitem').filter({ hasText: 'Product 2' });
await product.getByRole('button', { name: 'Add to cart' }).click();
```

### Handling Modals / Dialogs

Scope to a modal with `getByRole('dialog')` and query inside it. Check closure with `toBeHidden()`:

```ts
// Open
await page.getByRole('button', { name: 'New Project' }).click();
const dialog = page.getByRole('dialog');
await expect(dialog).toBeVisible();

// Interact within scope
await dialog.getByLabel('Name').fill('My Project');
await dialog.getByRole('button', { name: 'Save' }).click();

// Confirm closure (during fade-out animation, toBeHidden auto-retries)
await expect(dialog).toBeHidden();

// Verify the result outside
await expect(
  page.getByRole('list', { name: 'projects' }).getByRole('listitem').filter({ hasText: 'My Project' })
).toBeVisible();
```

`role="alertdialog"` is for warning dialogs (e.g., delete confirmation) via `getByRole('alertdialog')`.

## Assertions

Web-first assertions auto-retry:

```ts
await expect(page.getByText('Success')).toBeVisible();
await expect(page.getByRole('listitem')).toHaveCount(3);
await expect(page.getByTestId('status')).toHaveText('Done');
await expect(page).toHaveURL(/dashboard/);
await expect(page).toHaveTitle(/Home/);

// Soft assertion (test continues even on failure)
await expect.soft(page.getByTestId('count')).toHaveText('5');
```

## Reusing Authentication

```ts
// tests/auth.setup.ts
setup('authenticate', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill('user@test.com');
  await page.getByLabel('Password').fill('password');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await page.waitForURL('/dashboard');
  await page.context().storageState({ path: 'playwright/.auth/user.json' });
});
```

Tests that don't need auth: `test.use({ storageState: { cookies: [], origins: [] } })`

## File Operations

```ts
// Upload
await page.getByLabel('Upload').setInputFiles('myfile.pdf');

// From a buffer (no file needed)
await page.getByLabel('Upload').setInputFiles({
  name: 'file.txt', mimeType: 'text/plain', buffer: Buffer.from('content'),
});

// Download
const downloadPromise = page.waitForEvent('download');
await page.getByText('Download').click();
const download = await downloadPromise;
await download.saveAs('/tmp/file.pdf');
```

## Page Object Model

Keep it simple. Put assertions on the test side:

```ts
class LoginPage {
  constructor(private page: Page) {}
  readonly email = this.page.getByLabel('Email');
  readonly password = this.page.getByLabel('Password');
  readonly submit = this.page.getByRole('button', { name: 'Sign in' });

  async login(email: string, pass: string) {
    await this.email.fill(email);
    await this.password.fill(pass);
    await this.submit.click();
  }
}
```

## Debugging

```bash
npx playwright test --debug          # Launch Inspector
npx playwright test --ui             # UI mode (time-travel)
npx playwright test --trace on       # Generate trace
npx playwright show-report           # Show report
```

In code: `await page.pause()` opens the Inspector mid-test.
