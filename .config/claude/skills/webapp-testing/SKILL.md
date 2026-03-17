---
name: webapp-testing
description: Toolkit for interacting with and testing local web applications using agent-browser CLI. Supports verifying frontend functionality, debugging UI behavior, capturing browser screenshots, and viewing browser logs.
license: Complete terms in LICENSE.txt
---

# Web Application Testing

Use **agent-browser** CLI for all browser automation. It provides an accessibility-tree-based workflow optimized for AI agents.

**Prerequisites**: `agent-browser` installed globally (`npm install -g agent-browser && agent-browser install`)

## Decision Tree: Choosing Your Approach

```
User task → Is the server already running?
    ├─ Yes → Snapshot-first workflow:
    │        1. agent-browser open <url>
    │        2. agent-browser snapshot -c  (get semantic refs)
    │        3. Interact using @refs
    │        4. agent-browser close
    │
    ├─ No → Start server first, then snapshot-first:
    │        1. Start server in background (npm run dev &, etc.)
    │        2. Wait for port to be ready
    │        3. Follow snapshot-first workflow above
    │
    └─ Static HTML file?
        → agent-browser open file:///path/to/file.html
          Then follow snapshot-first workflow
```

## Core Workflow: Snapshot-First

Always start by getting the accessibility tree. This gives you semantic refs (`@e1`, `@e2`) for reliable element interaction.

```bash
# 1. Open target
agent-browser open http://localhost:3000

# 2. Get page structure
agent-browser snapshot -c
# Output:
#   - heading "Dashboard" [ref=e1] [level=1]
#   - button "Add Item" [ref=e2]
#   - textbox "Search" [ref=e3]
#   - link "Settings" [ref=e4]

# 3. Interact using refs
agent-browser click @e2
agent-browser fill @e3 "test query"
agent-browser press Enter

# 4. Verify result
agent-browser snapshot -c
agent-browser screenshot /tmp/result.png --full

# 5. Cleanup
agent-browser close
```

## Snapshot Variants

```bash
agent-browser snapshot              # full accessibility tree
agent-browser snapshot -i           # interactive elements only (buttons, inputs, links)
agent-browser snapshot -c           # compact (remove empty structural elements)
agent-browser snapshot -d 3         # limit tree depth
agent-browser snapshot -s "#main"   # scope to CSS selector
agent-browser snapshot -i -c        # combine: interactive + compact
```

## Element Discovery

Use `find` commands for semantic element lookup:

```bash
agent-browser find role button                    # all buttons
agent-browser find role button --name "Submit"    # button with specific name
agent-browser find text "Sign In"                 # by visible text
agent-browser find label "Email"                  # by associated label
agent-browser find placeholder "Search..."        # by placeholder text
agent-browser find role button click              # find and click in one command
agent-browser find label "Email" fill "user@test.com"  # find and fill
```

## Element Information

```bash
agent-browser get text @e1              # get text content
agent-browser get html @e1              # get inner HTML
agent-browser get attribute @e1 href    # get specific attribute
agent-browser get style @e1 color       # get computed style
agent-browser is visible @e1            # check visibility
agent-browser is enabled @e1            # check if enabled
agent-browser is checked @e1            # check checkbox state
```

## State Change Detection

Use diff to detect what changed after an action:

```bash
# Save baseline
agent-browser snapshot -c > /tmp/before.txt

# Perform action
agent-browser click @e2

# Compare
agent-browser diff snapshot --baseline /tmp/before.txt
```

## Authentication Persistence

```bash
# Login once, save state
agent-browser open http://localhost:3000/login
agent-browser fill @e1 "admin@example.com"
agent-browser fill @e2 "password"
agent-browser click @e3
agent-browser state save /tmp/auth-state.json

# Reuse in later sessions
agent-browser state load /tmp/auth-state.json
agent-browser open http://localhost:3000/dashboard
```

## Debugging

```bash
agent-browser console              # view console log messages
agent-browser console --clear      # view and clear
agent-browser errors               # view page errors
agent-browser errors --clear       # view and clear
agent-browser eval "document.title"  # run arbitrary JS
```

## Session Isolation

Use named sessions for parallel testing:

```bash
agent-browser --session test1 open http://localhost:3000
agent-browser --session test2 open http://localhost:3001
agent-browser --session test1 snapshot -c
agent-browser --session test2 snapshot -c
agent-browser --session test1 close
agent-browser --session test2 close
```

## Gotchas

- **Don't** use CSS selectors when `@ref` from snapshot is available — refs are more reliable
- **Don't** skip `snapshot` and guess element positions — always observe first
- **Do** use `snapshot -i` when you only care about interactive elements (faster, less noise)
- **Do** close the browser when done (`agent-browser close`) to free resources
- **snapshot が空**: ページのロード完了前に snapshot を取ると空になる。`agent-browser wait` でロード完了を待つこと
- **@ref の寿命**: ページ遷移やDOMの大きな変更で @ref は無効化される。操作前に必ず再 snapshot
- **ポート競合**: `npm run dev` が既にバックグラウンドで走っている場合、2重起動でポート競合する。`lsof -i :3000` で確認
- **file:// プロトコル制限**: file:// URL では CORS やいくつかの Web API が動作しない。localStorage 等のテストは http:// で
- **タイムアウト**: agent-browser のデフォルトタイムアウトは短い。SPA の初期ロードが遅い場合は明示的に wait を入れる

## Fallback: Python Playwright

For complex batch automation or CI scenarios where agent-browser is insufficient, fall back to Python Playwright scripts:

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('http://localhost:3000')
    page.wait_for_load_state('networkidle')
    # ... automation logic
    browser.close()
```

**Helper scripts** (for server lifecycle management):
- `scripts/with_server.py --help` — manages server startup/shutdown around automation scripts
