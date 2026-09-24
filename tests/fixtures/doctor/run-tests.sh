#!/usr/bin/env bash
# tests/fixtures/doctor/run-tests.sh
#
# Verify `task doctor` detects all 5 troubled scenarios from spec.
# Spec: docs/specs/2026-05-13-setup-doctor.md#acceptance-criteria (#6)
#
# Strategy: input-mock (PATH stubs + env override) + assertion (grep on output).
# We use contains-match (not full golden diff) to keep tests robust against
# path/hostname variation across machines.

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
cd "$REPO_ROOT"

DOCTOR="bash scripts/lifecycle/doctor.sh"
FIXT_DIR="tests/fixtures/doctor"
STUB_DIR="$REPO_ROOT/$FIXT_DIR/bin-stubs"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

PASS=0
FAIL=0

assert_contains() {
  local name="$1" output="$2" pattern="$3"
  if printf '%s' "$output" | grep -qE "$pattern"; then
    printf "  PASS  %s\n" "$name"
    PASS=$((PASS + 1))
  else
    printf "  FAIL  %s\n" "$name"
    printf "        expected pattern: %s\n" "$pattern"
    printf "        actual output:\n"
    printf '%s\n' "$output" | sed 's/^/        | /'
    FAIL=$((FAIL + 1))
  fi
}

echo "=== setup-doctor fixture tests ==="

# Build stub for rtk@0.35 (version drift)
mkdir -p "$STUB_DIR"
cat > "$STUB_DIR/rtk" <<'STUB'
#!/usr/bin/env bash
[[ "${1:-}" = "--version" ]] && { echo "rtk 0.35.0"; exit 0; }
exit 0
STUB
chmod +x "$STUB_DIR/rtk"

# ----- Scenario 1: rtk version drift (FAIL: 0.35 < 0.39) -----
out=$(PATH="$STUB_DIR:$PATH" $DOCTOR binary 2>&1 || true)
assert_contains "01-rtk-drift" "$out" '\[binary[[:space:]]*\] FAIL: rtk 0\.35\.0 found, requires >= 0\.39\.0'

# ----- Scenario 2: missing binary (FAIL: jq not found) -----
# Empty PATH to force lookup failure (keep /bin for awk/grep used inside doctor.sh)
out=$(PATH="/usr/bin:/bin" $DOCTOR binary 2>&1 || true)
assert_contains "02-binary-missing" "$out" '\[binary[[:space:]]*\] (FAIL|WARN): (rtk|jq|gh|task) (not found in PATH|not installed)'

# ----- Scenario 3: profile mismatch (WARN: hostname unknown) -----
out=$(SETUP_DOCTOR_HOSTNAME="unknown-host-xyz" $DOCTOR nix 2>&1 || true)
assert_contains "03-profile-mismatch" "$out" '\[nix[[:space:]]*\] WARN: hostname=unknown-host-xyz does not match'

# ----- Scenario 4: hook with unresolvable command -----
cat > "$TMP/bad-settings.json" <<'JSON'
{
  "hooks": {
    "PreToolUse": [
      {
        "hooks": [
          { "type": "command", "command": "this-binary-does-not-exist-xyz" }
        ]
      }
    ]
  }
}
JSON
out=$(SETUP_DOCTOR_SETTINGS="$TMP/bad-settings.json" $DOCTOR hook 2>&1 || true)
assert_contains "04-hook-unresolvable" "$out" '\[hook[[:space:]]*\] FAIL: no resolvable executable in hook'

# ----- Scenario 5: brew formula drift (declared but not installed) -----
cat > "$TMP/extra-brew.nix" <<'NIX'
{
  homebrew = {
    brews = [
      "this-formula-definitely-does-not-exist-xyz"
    ];
  };
}
NIX
out=$(SETUP_DOCTOR_NIX_FILE="$TMP/extra-brew.nix" $DOCTOR brew 2>&1 || true)
assert_contains "05-brew-formula-drift" "$out" '\[brew[[:space:]]*\] FAIL: this-formula-definitely-does-not-exist-xyz declared in nix\.brews but not installed'

# ----- Scenario 6: invalid settings.json -> hook FAIL (not silent OK) -----
printf '{ this is not json' > "$TMP/broken-settings.json"
out=$(SETUP_DOCTOR_SETTINGS="$TMP/broken-settings.json" $DOCTOR hook 2>&1 || true)
assert_contains "06-hook-invalid-json" "$out" '\[hook[[:space:]]*\] FAIL: settings\.json is not valid JSON'

# ----- Scenario 7: brew tap drift (declared but not tapped) -----
cat > "$TMP/extra-tap.nix" <<'NIX'
{
  homebrew = {
    taps = [
      "nonexistent-org/nonexistent-tap-xyz"
    ];
  };
}
NIX
out=$(SETUP_DOCTOR_NIX_FILE="$TMP/extra-tap.nix" $DOCTOR brew 2>&1 || true)
assert_contains "07-brew-tap-drift" "$out" '\[brew[[:space:]]*\] FAIL: nonexistent-org/nonexistent-tap-xyz declared in nix\.taps but not tapped'

# ----- Scenario 8: live settings replaced wholesale -> repo-owned keys FAIL -----
# The real incident: ~/.claude/settings.json shrank to a runtime-written stub,
# silently disabling permissions/hooks/plugins while skills kept working.
cat > "$TMP/repo-settings.json" <<'JSON'
{ "permissions": {}, "hooks": {}, "enabledPlugins": {}, "model": "opus" }
JSON
printf '{ "tui": "fullscreen" }' > "$TMP/stub-settings.json"
out=$(SETUP_DOCTOR_REPO_SETTINGS="$TMP/repo-settings.json" \
      SETUP_DOCTOR_SETTINGS="$TMP/stub-settings.json" $DOCTOR settings 2>&1 || true)
assert_contains "08-settings-wholesale-drift" "$out" "\[settings\] FAIL: repo-owned key 'permissions' absent from live settings"

# ----- Scenario 9: runtime-owned key absent -> WARN, never FAIL -----
# Picking the default in `/model` deletes the `model` key outright. Failing on
# that would fire on ordinary use and train the check to be ignored.
cat > "$TMP/live-no-model.json" <<'JSON'
{ "permissions": {}, "hooks": {}, "enabledPlugins": {} }
JSON
out=$(SETUP_DOCTOR_REPO_SETTINGS="$TMP/repo-settings.json" \
      SETUP_DOCTOR_SETTINGS="$TMP/live-no-model.json" $DOCTOR settings 2>&1 || true)
assert_contains "09-settings-runtime-key-warn" "$out" '\[settings\] WARN: repo keys absent from live: model'
assert_contains "09b-settings-no-false-fail" "$out" 'Summary: FAIL=0'

# ----- Scenario 10: permissions present but contents drifted -> FAIL per tier -----
# The real drift (2026-09-24): live lacked 8 pnpm/bun ask rules while allowing
# `pnpm *`, so `pnpm add` ran unprompted — and key presence alone reported OK.
cat > "$TMP/repo-perm.json" <<'JSON'
{ "permissions": { "allow": ["Bash(pnpm *)", "Bash(agy *)"], "ask": ["Bash(pnpm add *)"],
  "deny": ["Bash(rm -rf *)"], "disableBypassPermissionsMode": "disable" } }
JSON
cat > "$TMP/live-perm-drift.json" <<'JSON'
{ "permissions": { "allow": ["Bash(pnpm *)", "Bash(gemini *)"],
  "deny": ["Bash(rm -rf *)"] }, "hooks": {} }
JSON
out=$(SETUP_DOCTOR_REPO_SETTINGS="$TMP/repo-perm.json" \
      SETUP_DOCTOR_SETTINGS="$TMP/live-perm-drift.json" $DOCTOR settings 2>&1 || true)
assert_contains "10-perm-allow-drift" "$out" '\[settings\] FAIL: permissions\.allow drifted from repo \(repo-only: Bash\(agy \*\); live-only: Bash\(gemini \*\)\)'
assert_contains "10b-perm-ask-missing" "$out" '\[settings\] FAIL: permissions\.ask drifted from repo \(repo-only: Bash\(pnpm add \*\); live-only: -\)'
assert_contains "10c-perm-scalar-drift" "$out" '\[settings\] FAIL: permissions\.disableBypassPermissionsMode drifted from repo \(repo: "disable"; live: absent\)'

# ----- Scenario 11: same rules in a different order -> OK, not FAIL -----
cat > "$TMP/live-perm-reordered.json" <<'JSON'
{ "permissions": { "disableBypassPermissionsMode": "disable", "deny": ["Bash(rm -rf *)"],
  "ask": ["Bash(pnpm add *)"], "allow": ["Bash(agy *)", "Bash(pnpm *)"] } }
JSON
out=$(SETUP_DOCTOR_REPO_SETTINGS="$TMP/repo-perm.json" \
      SETUP_DOCTOR_SETTINGS="$TMP/live-perm-reordered.json" $DOCTOR settings 2>&1 || true)
assert_contains "11-perm-order-insensitive" "$out" '\[settings\] OK: permissions match repo'
assert_contains "11b-perm-no-false-fail" "$out" 'Summary: FAIL=0'

# ----- Scenario 12: sync replaces permissions only, keeps injected hooks -----
SYNC="bash scripts/lifecycle/claude-settings-sync-permissions.sh"
cat > "$TMP/live-sync.json" <<'JSON'
{ "permissions": { "allow": ["Bash(gemini *)"] },
  "hooks": { "Stop": [{ "hooks": [{ "type": "command", "command": "orca-hook.sh" }] }] },
  "autoMode": "on" }
JSON
out=$(CLAUDE_SETTINGS_REPO="$TMP/repo-perm.json" CLAUDE_SETTINGS_LIVE="$TMP/live-sync.json" \
      $SYNC --yes 2>&1 || true)
assert_contains "12-sync-reports-drift" "$out" 'permissions\.allow drifted from repo'
out=$(SETUP_DOCTOR_REPO_SETTINGS="$TMP/repo-perm.json" \
      SETUP_DOCTOR_SETTINGS="$TMP/live-sync.json" $DOCTOR settings 2>&1 || true)
assert_contains "12b-sync-then-doctor-ok" "$out" '\[settings\] OK: permissions match repo'
assert_contains "12c-sync-keeps-hooks" "$(jq -c '[.hooks.Stop[0].hooks[0].command, .autoMode]' "$TMP/live-sync.json")" '^\["orca-hook\.sh","on"\]$'
assert_contains "12d-sync-backup" "$(ls "$TMP")" '^live-sync\.json\.bak-[0-9]'

# ----- Scenario 13: no --yes and no terminal -> refuse, leave live untouched -----
cp "$TMP/live-perm-drift.json" "$TMP/live-noconfirm.json"
out=$(CLAUDE_SETTINGS_REPO="$TMP/repo-perm.json" CLAUDE_SETTINGS_LIVE="$TMP/live-noconfirm.json" \
      $SYNC < /dev/null 2>&1; echo "exit=$?")
assert_contains "13-sync-refuses-without-confirm" "$out" 'exit=[1-9]'
cmp -s "$TMP/live-perm-drift.json" "$TMP/live-noconfirm.json" && same=yes || same=no
assert_contains "13b-sync-live-untouched" "$same" '^yes$'

# ----- Scenario 14: already in sync -> no write, exit 0 -----
out=$(CLAUDE_SETTINGS_REPO="$TMP/repo-perm.json" CLAUDE_SETTINGS_LIVE="$TMP/live-perm-reordered.json" \
      $SYNC --yes 2>&1; echo "exit=$?")
assert_contains "14-sync-noop-when-in-sync" "$out" 'already in sync'
assert_contains "14b-sync-noop-exit0" "$out" 'exit=0'

# ----- Scenario 15: malformed permissions types -> FAIL, never "match" -----
# jq subtraction on a string, or null vs [], must not collapse into OK.
printf '{ "permissions": { "allow": ["Bash(pnpm *)", "Bash(agy *)"], "ask": "Bash(pnpm add *)", "deny": ["Bash(rm -rf *)"], "disableBypassPermissionsMode": "disable" } }' \
  > "$TMP/live-perm-string.json"
out=$(SETUP_DOCTOR_REPO_SETTINGS="$TMP/repo-perm.json" \
      SETUP_DOCTOR_SETTINGS="$TMP/live-perm-string.json" $DOCTOR settings 2>&1 || true)
assert_contains "15-perm-type-mismatch" "$out" '\[settings\] FAIL: permissions\.ask is not an array in live settings \(string\)'
printf '{ "permissions": null }' > "$TMP/live-perm-null.json"
out=$(SETUP_DOCTOR_REPO_SETTINGS="$TMP/repo-perm.json" \
      SETUP_DOCTOR_SETTINGS="$TMP/live-perm-null.json" $DOCTOR settings 2>&1 || true)
assert_contains "15b-perm-null-block" "$out" '\[settings\] FAIL: permissions is not an object in live settings \(null\)'
out=$(CLAUDE_SETTINGS_REPO="$TMP/repo-perm.json" CLAUDE_SETTINGS_LIVE="$TMP/live-perm-null.json" \
      $SYNC --yes 2>&1; echo "exit=$?")
assert_contains "15c-sync-repairs-null" "$out" 'synced permissions'
out=$(SETUP_DOCTOR_REPO_SETTINGS="$TMP/repo-perm.json" \
      SETUP_DOCTOR_SETTINGS="$TMP/live-perm-null.json" $DOCTOR settings 2>&1 || true)
assert_contains "15d-null-repaired" "$out" '\[settings\] OK: permissions match repo'

# ----- Scenario 15e: explicit null tier vs array -> FAIL; absent tier vs [] -> OK -----
printf '{ "permissions": { "allow": ["Bash(pnpm *)", "Bash(agy *)"], "ask": null, "deny": ["Bash(rm -rf *)"], "disableBypassPermissionsMode": "disable" } }' \
  > "$TMP/live-ask-null.json"
out=$(SETUP_DOCTOR_REPO_SETTINGS="$TMP/repo-perm.json" \
      SETUP_DOCTOR_SETTINGS="$TMP/live-ask-null.json" $DOCTOR settings 2>&1 || true)
assert_contains "15e-explicit-null-tier" "$out" '\[settings\] FAIL: permissions\.ask is not an array in live settings \(null\)'
printf '{ "permissions": { "allow": ["Bash(x *)"], "ask": [] } }' > "$TMP/repo-empty-ask.json"
printf '{ "permissions": { "allow": ["Bash(x *)"] } }' > "$TMP/live-absent-ask.json"
out=$(SETUP_DOCTOR_REPO_SETTINGS="$TMP/repo-empty-ask.json" \
      SETUP_DOCTOR_SETTINGS="$TMP/live-absent-ask.json" $DOCTOR settings 2>&1 || true)
assert_contains "15f-absent-tier-equals-empty" "$out" '\[settings\] OK: permissions match repo'
printf '{ "permissions": { "allow": ["Bash(x *)"], "ask": null } }' > "$TMP/live-null-ask.json"
out=$(SETUP_DOCTOR_REPO_SETTINGS="$TMP/live-absent-ask.json" \
      SETUP_DOCTOR_SETTINGS="$TMP/live-null-ask.json" $DOCTOR settings 2>&1 || true)
assert_contains "15g-absent-vs-null" "$out" '\[settings\] FAIL: permissions\.ask is not an array in live settings \(null\)'
out=$(SETUP_DOCTOR_REPO_SETTINGS="$TMP/live-null-ask.json" \
      SETUP_DOCTOR_SETTINGS="$TMP/live-absent-ask.json" $DOCTOR settings 2>&1 || true)
assert_contains "15h-null-vs-absent" "$out" '\[settings\] FAIL: permissions\.ask is not an array in repo settings \(null\)'

# ----- Scenario 15i: SAME malformed tier on both sides -> FAIL, not "match" -----
printf '{ "permissions": { "allow": "Bash(x *)", "ask": null } }' > "$TMP/both-bad-repo.json"
cp "$TMP/both-bad-repo.json" "$TMP/both-bad-live.json"
out=$(SETUP_DOCTOR_REPO_SETTINGS="$TMP/both-bad-repo.json" \
      SETUP_DOCTOR_SETTINGS="$TMP/both-bad-live.json" $DOCTOR settings 2>&1 || true)
assert_contains "15i-equal-malformed-repo" "$out" '\[settings\] FAIL: permissions\.allow is not an array in repo settings \(string\)'
assert_contains "15j-equal-malformed-live" "$out" '\[settings\] FAIL: permissions\.ask is not an array in live settings \(null\)'
assert_contains "15k-equal-malformed-no-match" "$(printf '%s' "$out" | grep -c 'permissions match repo')" '^0$'
out=$(CLAUDE_SETTINGS_REPO="$TMP/both-bad-repo.json" CLAUDE_SETTINGS_LIVE="$TMP/both-bad-live.json" \
      $SYNC --yes 2>&1; echo "exit=$?")
assert_contains "15l-sync-refuses-malformed-repo-tier" "$out" 'exit=[1-9]'

# ----- Scenario 16: broken REPO permissions -> doctor FAIL, sync refuses -----
# The repo is the source; a sync from a broken repo would push the breakage live.
printf '{ "permissions": null }' > "$TMP/repo-perm-null.json"
printf '{ "hooks": {} }' > "$TMP/repo-no-perm.json"
out=$(SETUP_DOCTOR_REPO_SETTINGS="$TMP/repo-perm-null.json" \
      SETUP_DOCTOR_SETTINGS="$TMP/live-perm-drift.json" $DOCTOR settings 2>&1 || true)
assert_contains "16-repo-perm-null" "$out" '\[settings\] FAIL: permissions is not an object in repo settings \(null\)'
out=$(SETUP_DOCTOR_REPO_SETTINGS="$TMP/repo-no-perm.json" \
      SETUP_DOCTOR_SETTINGS="$TMP/live-perm-drift.json" $DOCTOR settings 2>&1 || true)
assert_contains "16b-repo-perm-missing" "$out" '\[settings\] FAIL: repo settings has no permissions block'
cp "$TMP/live-perm-drift.json" "$TMP/live-from-broken-repo.json"
out=$(CLAUDE_SETTINGS_REPO="$TMP/repo-perm-null.json" CLAUDE_SETTINGS_LIVE="$TMP/live-from-broken-repo.json" \
      $SYNC --yes 2>&1; echo "exit=$?")
assert_contains "16c-sync-refuses-broken-repo" "$out" 'exit=[1-9]'
cmp -s "$TMP/live-perm-drift.json" "$TMP/live-from-broken-repo.json" && same=yes || same=no
assert_contains "16d-live-untouched-by-broken-repo" "$same" '^yes$'

echo
echo "=== Summary: PASS=$PASS FAIL=$FAIL ==="
[[ $FAIL -eq 0 ]] || exit 1
