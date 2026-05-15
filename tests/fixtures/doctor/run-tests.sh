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

echo
echo "=== Summary: PASS=$PASS FAIL=$FAIL ==="
[[ $FAIL -eq 0 ]] || exit 1
