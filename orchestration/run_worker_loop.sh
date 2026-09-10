#!/bin/bash
# run_worker_loop.sh — wraps a headless CLI agent in the WORKER_LOOP.md protocol
# so it actually loops unattended, instead of sitting idle in a chat panel.
#
# Usage:
#   ./run_worker_loop.sh <AGENT_NAME> <BACKEND> [REPO_DIR]
#
#   AGENT_NAME  one of: poly-bot | poster-studio | win-agy | agent-farm
#   BACKEND     one of: codex | agy | claude
#   REPO_DIR    working directory for the CLI (default: ~/<AGENT_NAME>)
#
# Examples:
#   ./run_worker_loop.sh poly-bot codex
#   ./run_worker_loop.sh poster-studio agy
#
# Runs in the FOREGROUND by default so you can watch it. To background it:
#   nohup ./run_worker_loop.sh poly-bot codex > ~/.agentic/poly-bot.loop.log 2>&1 &
#   disown
# Stop it: put a line starting "STOP" in the agent's inbox (checked each
# iteration) or Ctrl-C / kill the pid if backgrounded.
set -u

AGENT="${1:?usage: run_worker_loop.sh <agent-name> <codex|agy|claude> [repo-dir]}"
BACKEND="${2:?usage: run_worker_loop.sh <agent-name> <codex|agy|claude> [repo-dir]}"
REPO="${3:-$HOME/$AGENT}"
BOARD="$HOME/.agentic/board"
CONTRACT="$BOARD/WORKER_LOOP.md"
# codex is not on PATH by default - it lives inside the VS Code extension dir.
# Override with: CODEX_BIN=/path/to/codex ./run_worker_loop.sh ...
CODEX_BIN="${CODEX_BIN:-$(ls -d "$HOME"/.vscode-server/extensions/openai.chatgpt-*/bin/linux-x86_64/codex 2>/dev/null | tail -1)}"
MAX_HOURS=6
started=$(date +%s)
iter=0
idle_streak=0
fail_streak=0

log() { echo "$(date -uIs) [$AGENT] $1"; }

[ -d "$REPO" ] || { echo "ERROR: repo dir $REPO does not exist"; exit 1; }
[ -f "$CONTRACT" ] || { echo "ERROR: $CONTRACT not found"; exit 1; }

log "starting worker loop, backend=$BACKEND, repo=$REPO"

while true; do
  iter=$((iter+1))
  elapsed=$(( $(date +%s) - started ))
  if [ "$elapsed" -gt $((MAX_HOURS*3600)) ]; then
    log "hit ${MAX_HOURS}h bound after $iter iterations - exiting for a clean restart"
    exit 0
  fi

  # health check
  wsl_free=$(free -m | awk 'NR==2{print $7}')
  if [ "${wsl_free:-0}" -lt 1500 ]; then
    log "WSL free ${wsl_free}MB < 1500MB - sleeping 900s"
    sleep 900
    continue
  fi
  stuck=$(python3 /mnt/c/Agents/agentic-universe/repo/tools/orphan_scan.py concerning 2>/dev/null || echo 0)
  if [ "${stuck:-0}" -gt 0 ]; then
    log "$stuck concerning session(s) present - sleeping 900s (reap manually if it persists)"
    sleep 900
    continue
  fi

  # owner STOP switch
  if grep -q '^STOP' "$BOARD/inbox/$AGENT.md" 2>/dev/null; then
    log "STOP found in inbox - exiting"
    exit 0
  fi

  prompt=$(cat "$CONTRACT"; echo; echo "---"; echo "Your AGENT name is: $AGENT"; echo "Do one iteration of the loop now, then stop (this wrapper re-invokes you).")

  log "iteration $iter: dispatching one turn via $BACKEND"
  case "$BACKEND" in
    codex)
      [ -x "$CODEX_BIN" ] || { echo "codex binary not found - set CODEX_BIN"; exit 1; }
      out=$(cd "$REPO" && "$CODEX_BIN" exec -s workspace-write "$prompt" 2>&1)
      ;;
    agy)
      out=$(cd "$REPO" && AGY_LAUNCHED_VIA_WRAPPER=1 /home/dev/.local/bin/agy-real \
            --print --mode accept-edits --print-timeout 1200s "$prompt" 2>&1)
      ;;
    claude)
      out=$(cd "$REPO" && claude -p "$prompt" --permission-mode acceptEdits 2>&1)
      ;;
    *)
      echo "unknown backend: $BACKEND (use codex|agy|claude)"; exit 1 ;;
  esac
  rc=$?
  tail1=$(echo "$out" | tail -1)
  log "iteration $iter rc=$rc: ${tail1:0:200}"

  if [ "$rc" -ne 0 ]; then
    fail_streak=$((fail_streak+1))
    if [ "$fail_streak" -ge 3 ]; then
      log "3 consecutive failures - exiting, needs a human look"
      exit 1
    fi
    sleep 300
    continue
  fi
  fail_streak=0

  # crude IDLE detection: did the last outbox line change this iteration?
  last_line=$(grep -E '^## ' "$BOARD/outbox/$AGENT.md" 2>/dev/null | tail -1)
  if [ "$last_line" = "${prev_last_line:-}" ]; then
    idle_streak=$((idle_streak+1))
  else
    idle_streak=0
  fi
  prev_last_line="$last_line"

  if [ "$idle_streak" -ge 3 ]; then
    log "3 consecutive IDLE iterations - sleeping 1800s"
    sleep 1800
  else
    sleep 60
  fi
done
