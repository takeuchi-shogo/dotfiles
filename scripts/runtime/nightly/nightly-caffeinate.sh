#!/usr/bin/env bash
# nightly-caffeinate.sh — 夜間バッチ枠の覚醒維持アンブレラ。
#
# pmset scheduled wake (setup-nightly-wake.sh) で起きた Mac を、バッチ完了まで
# 眠らせない。pmset の `sleep 1` (1分アイドルで即スリープ) のままだと、起床直後に
# 再スリープして staggered ジョブ群が走らないため、覚醒維持の assertion を張る。
#
# launchd com.user.nightly.caffeinate が wake 時刻に発火しこれを起動する。
# 注意: caffeinate 単独ではスリープ中の Mac を起こせない。起床は pmset が担う (役割分担)。
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=./nightly-wake.env
source "${SCRIPT_DIR}/nightly-wake.env"

SECS="${NIGHTLY_CAFFEINATE_SECONDS:-10800}"
[[ "$SECS" =~ ^[0-9]+$ ]] && (( SECS > 0 )) \
    || { echo "[nightly-caffeinate] FATAL: NIGHTLY_CAFFEINATE_SECONDS must be a positive integer (got: '$SECS')" >&2; exit 1; }

echo "[nightly-caffeinate] hold awake for ${SECS}s at $(date '+%Y-%m-%dT%H:%M:%S%z')"
# -i: idle sleep 抑止 / -s: system sleep 抑止 (AC 接続時のみ有効) / -t: 指定秒で自動失効
exec caffeinate -i -s -t "$SECS"
