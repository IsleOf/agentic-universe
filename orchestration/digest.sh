#!/bin/bash
# digest.sh - one-screen fleet status. Read-only, no LLM, ~instant.
# Run it directly: bash /home/dev/.agentic/digest.sh
# Or watch it live:  watch -n 30 bash /home/dev/.agentic/digest.sh
set -u
A=~/.agentic
B="$A/board"

echo "================ AGENTIC UNIVERSE FLEET DIGEST ================"
date -u +"  %Y-%m-%d %H:%M:%SZ"
echo

echo "-- RESOURCES --"
free -m | awk 'NR==2{printf "  WSL free: %s MB / %s MB total\n",$7,$2}'
WIN=$(powershell.exe -NoProfile -Command '[math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1024)' 2>/dev/null | tr -d '\r')
echo "  Windows free: ${WIN:-?} MB"
STUCK=$(python3 /mnt/c/Agents/agentic-universe/repo/tools/orphan_scan.py concerning 2>/dev/null || echo "?")
echo "  Stuck sessions (concerning): $STUCK"
echo

echo "-- CONDUCTOR --"
if bash "$A/guard.sh" >/dev/null 2>&1; then echo "  guard: OK (can dispatch)"; else echo "  guard: BLOCKED"; fi
[ -f "$A/worker.lock" ] && echo "  worker: RUNNING since $(cat "$A/worker.lock")" || echo "  worker: idle"
echo "  last 3 log lines:"
tail -3 "$A/conductor.log" 2>/dev/null | sed 's/^/    /'
echo

echo "-- QUEUE (next unblocked task) --"
python3 - <<'PY' 2>/dev/null
import sys, re, pathlib
sys.path.insert(0, "/home/dev/.agentic")
q = pathlib.Path("/home/dev/.agentic/QUEUE.md").read_text(encoding="utf-8")
for block in re.split(r"(?=^## TASK )", q, flags=re.M):
    if not block.startswith("## TASK "): continue
    m = re.search(r"^blocked:[ \t]*(.*)$", block, flags=re.M)
    if m and m.group(1).strip().lower() in ("", "none", "-"):
        print("  " + block.split("\n", 1)[0].replace("## TASK ", ""))
        break
else:
    print("  (queue empty or all blocked)")
PY
echo

echo "-- AETHER (port 8317) --"
if curl -s --max-time 2 http://127.0.0.1:8317/v1/models >/dev/null 2>&1; then
  echo "  UP, reachable from WSL"
else
  echo "  NOT reachable from WSL (bx-12) - may still be up for Windows apps (Hermes); check from Windows separately"
fi
echo

echo "-- AGENTS (last outbox line each) --"
for f in "$B"/outbox/*.md; do
  name=$(basename "$f" .md)
  [ "$name" = "conductor" ] && continue
  last=$(grep -E '^(DID|DONE|FAILED|PUSHBACK|ACK):?|^DONE |^FAILED |^PUSHBACK ' "$f" 2>/dev/null | tail -1)
  ts=$(grep '^## ' "$f" 2>/dev/null | tail -1)
  printf "  %-14s %s\n" "$name" "${ts:-(no reports)}"
  [ -n "$last" ] && printf "  %-14s   %s\n" "" "${last:0:110}"
done
echo

echo "-- LIVE agy/codex/claude PROCESSES --"
python3 /mnt/c/Agents/agentic-universe/repo/tools/orphan_scan.py scan 2>/dev/null | head -12
echo "=================================================================="
