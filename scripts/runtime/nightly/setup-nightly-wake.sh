#!/usr/bin/env bash
# setup-nightly-wake.sh — 夜間バッチ枠の scheduled wake を冪等適用 (pmset)。
#
# macOS の pmset は宣言的設定ファイルを持たないため、git 管理した nightly-wake.env の
# 時刻をこのスクリプトで適用する。別 PC 再現は `task nightly:wake`。
#
# 前提 (正直に): ノート (MacBook) では AC 接続時のみ scheduled wake が確実に有効。
# バッテリー駆動時は womp 抑制で起床しないことがある。夜は電源接続 + 蓋を閉じない
# (または外部ディスプレイ) こと。これは OS/ハード制約でコード回避不能。
#
# pmset repeat は wake の繰り返しスケジュールを 1 枠だけ持つ。apply は既存 repeat を
# 上書きする (冪等)。cancel は全 repeat イベントを解除する点に注意。
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=./nightly-wake.env
source "${SCRIPT_DIR}/nightly-wake.env"

[[ "${NIGHTLY_WAKE_HOUR:-}" =~ ^[0-9]+$ ]] && (( NIGHTLY_WAKE_HOUR <= 23 )) \
    || { echo "[FATAL] NIGHTLY_WAKE_HOUR must be an integer 0-23 (got: '${NIGHTLY_WAKE_HOUR:-}')" >&2; exit 1; }
[[ "${NIGHTLY_WAKE_MINUTE:-}" =~ ^[0-9]+$ ]] && (( NIGHTLY_WAKE_MINUTE <= 59 )) \
    || { echo "[FATAL] NIGHTLY_WAKE_MINUTE must be an integer 0-59 (got: '${NIGHTLY_WAKE_MINUTE:-}')" >&2; exit 1; }

HH=$(printf '%02d' "$NIGHTLY_WAKE_HOUR")
MM=$(printf '%02d' "$NIGHTLY_WAKE_MINUTE")
CMD="${1:-apply}"

case "$CMD" in
    apply)
        echo "[nightly-wake] applying: pmset repeat wakeorpoweron MTWRFSU ${HH}:${MM}:00 (要 sudo)"
        sudo pmset repeat wakeorpoweron MTWRFSU "${HH}:${MM}:00"
        echo "[nightly-wake] done. current schedule:"
        pmset -g sched
        ;;
    cancel)
        echo "[nightly-wake] cancelling all repeating power events: pmset repeat cancel (要 sudo)"
        sudo pmset repeat cancel
        ;;
    status)
        pmset -g sched
        ;;
    *)
        echo "usage: $0 {apply|cancel|status}" >&2
        exit 2
        ;;
esac
