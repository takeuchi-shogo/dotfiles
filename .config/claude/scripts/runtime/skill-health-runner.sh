#!/usr/bin/env bash
# LaunchAgent から呼ばれるラッパー。各 script は内部で idempotent gate を持つ。
# ログイン毎に発火、cron との二重起動でもレポートは 1 日 1 つしか作られない。

set -uo pipefail

bash "$HOME/.claude/scripts/runtime/probation-30day.sh" || true
bash "$HOME/.claude/scripts/runtime/skill-usage-weekly.sh" || true
bash "$HOME/.claude/scripts/runtime/skill-count-alert.sh" || true
