#!/usr/bin/env bash
# cmux_resolver.sh — secure CMUX CLI resolution (CWE-426 / CWE-427)
# Priority: $CMUX_CLI env → /Applications/cmux.app/.../cmux → fail-closed (no PATH search)
# Validation: absolute path, executable, regular file, non-symlink (rejects all symlinks)
# Homebrew/Nix/asdf: set $CMUX_CLI to a canonical absolute path (their bin/ is a symlink)
# Out of scope: user uid compromise, TOCTOU race between validation and execve

_resolve_cmux_cli() {
    if [[ -n "${CMUX_CLI:-}" ]]; then
        if [[ "$CMUX_CLI" = /* ]] \
           && [[ -x "$CMUX_CLI" ]] \
           && [[ ! -d "$CMUX_CLI" ]] \
           && [[ ! -L "$CMUX_CLI" ]]; then
            printf '%s\n' "$CMUX_CLI"
            return 0
        fi
        echo "[cmux_resolver] CMUX_CLI rejected (need absolute, executable, regular, non-symlink): $CMUX_CLI" >&2
        return 1
    fi

    local c
    for c in \
        "/Applications/cmux.app/Contents/Resources/bin/cmux"; do
        if [[ -x "$c" ]] && [[ ! -d "$c" ]] && [[ ! -L "$c" ]]; then
            printf '%s\n' "$c"
            return 0
        fi
    done

    echo "[cmux_resolver] cmux not found at /Applications/cmux.app/Contents/Resources/bin/cmux. Set \$CMUX_CLI to a canonical absolute path for non-standard installs." >&2
    return 1
}
