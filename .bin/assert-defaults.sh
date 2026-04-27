#!/usr/bin/env bash
# assert-defaults.sh — Phase C minimum版 (C0 用)
#
# nix で宣言した system.defaults.<domain>.<key> が実 macOS の `defaults read` と
# 一致するかを assertion する。C1 で domain 全体対応の full 版に拡張予定。
#
# Usage:
#   assert-defaults.sh <host> <domain> <key> <expected>
#   assert-defaults.sh <host> <domain> <key> --absent
#
# Exit codes:
#   0 — 一致
#   1 — 不一致 (MISMATCH)
#   2 — 引数エラー
set -euo pipefail

usage() {
  cat >&2 <<EOF
Usage: $0 <host> <domain> <key> <expected>
       $0 <host> <domain> <key> --absent

Examples:
  $0 private NSGlobalDomain AppleShowAllExtensions 1
  $0 private NSGlobalDomain AppleShowAllExtensions --absent
EOF
  exit 2
}

if [ "$#" -ne 4 ]; then
  usage
fi

HOST="$1"
DOMAIN="$2"
KEY="$3"
EXPECTED="$4"

# host は今のところ表示のみ (将来 docs/inventory/<host>/ 切替に使う)
: "$HOST"

actual=$(defaults read "$DOMAIN" "$KEY" 2>&1 || true)

if [[ "$actual" == *"does not exist"* ]]; then
  if [ "$EXPECTED" = "--absent" ]; then
    echo "PASS: $DOMAIN.$KEY is absent (as expected)"
    exit 0
  fi
  echo "MISMATCH: $DOMAIN.$KEY is absent, expected '$EXPECTED'" >&2
  exit 1
fi

if [ "$EXPECTED" = "--absent" ]; then
  echo "MISMATCH: $DOMAIN.$KEY = '$actual', expected absent" >&2
  exit 1
fi

if [ "$actual" = "$EXPECTED" ]; then
  echo "PASS: $DOMAIN.$KEY = '$actual'"
  exit 0
fi

echo "MISMATCH: $DOMAIN.$KEY = '$actual', expected '$EXPECTED'" >&2
exit 1
