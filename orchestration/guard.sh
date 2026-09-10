#!/bin/bash
# guard.sh - gate for the autonomous conductor.
# exit 0 = safe to dispatch a worker; exit 1 = skip this run (logged, not fatal).
#
# This is what makes an autonomous cron safe on a box that has leaked to <1GB free
# twice today: a sick machine auto-pauses the build-out instead of accelerating
# into the wall.
set -u
AGENTIC="$HOME/.agentic"
REPO="/mnt/c/Agents/agentic-universe/repo"
MIN_WSL_MB=1500
MIN_WIN_MB=1500

log() { echo "$(date -uIs) guard: $1" >> "$AGENTIC/guard.log"; }
fail() { log "SKIP - $1"; exit 1; }

# 1. WSL available memory
wsl_free=$(free -m | awk 'NR==2{print $7}')
[ "${wsl_free:-0}" -lt "$MIN_WSL_MB" ] && fail "WSL avail ${wsl_free}MB < ${MIN_WSL_MB}MB"

# 2. Windows free memory (cheap powershell call, ~1s)
win_free=$(powershell.exe -NoProfile -Command \
  '[math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1024)' \
  2>/dev/null | tr -d '\r ')
if [ -n "${win_free:-}" ]; then
  [ "$win_free" -lt "$MIN_WIN_MB" ] && fail "Windows free ${win_free}MB < ${MIN_WIN_MB}MB"
fi

# 3. no stuck agent sessions (the four-instances-in-one-day failure)
if [ -f "$REPO/tools/orphan_scan.py" ]; then
  flagged=$(python3 "$REPO/tools/orphan_scan.py" scan 2>/dev/null \
    | grep -cE 'idle_prompted_but_busy|spinning' || true)
  [ "${flagged:-0}" -gt 0 ] && fail "${flagged} flagged session(s) present - reap first"
fi

# 4. a worker already running
[ -f "$AGENTIC/worker.lock" ] && fail "worker.lock present (previous worker not done)"

log "OK (wsl ${wsl_free}MB / win ${win_free:-?}MB)"
exit 0
