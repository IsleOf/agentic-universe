#!/usr/bin/env python3
"""dashboard.py — generates dashboard.html, a one-page fleet view. No deps.

Run once:   python3 /home/dev/.agentic/dashboard.py
Serve it:   python3 -m http.server 8899 --directory /home/dev/.agentic
Then open (from Windows):  http://localhost:8899/dashboard.html

Or just open the file directly in a browser without serving it:
  file://///wsl$/Ubuntu/home/dev/.agentic/dashboard.html
(serving is nicer because the meta-refresh below then re-fetches live data)

Regenerate on a cron for a "live" page: */2 * * * * python3 dashboard.py
"""
import html
import json
import pathlib
import re
import subprocess
import time

A = pathlib.Path.home() / ".agentic"
B = A / "board"
OUT = A / "dashboard.html"


def sh(cmd, timeout=5):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip()
    except Exception as e:
        return "(error: %s)" % e


def mem():
    wsl = sh(["bash", "-c", "free -m | awk 'NR==2{print $7}'"])
    win = sh(["powershell.exe", "-NoProfile", "-Command",
             "[math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1024)"])
    return wsl, win.strip()


def guard_state():
    r = subprocess.run(["bash", str(A / "guard.sh")], capture_output=True, text=True)
    return "OK" if r.returncode == 0 else "BLOCKED"


def next_task():
    q = A / "QUEUE.md"
    if not q.exists():
        return "(no queue)"
    text = q.read_text(encoding="utf-8")
    for block in re.split(r"(?=^## TASK )", text, flags=re.M):
        if not block.startswith("## TASK "):
            continue
        m = re.search(r"^blocked:[ \t]*(.*)$", block, flags=re.M)
        if m and m.group(1).strip().lower() in ("", "none", "-"):
            return block.split("\n", 1)[0].replace("## TASK ", "")
    return "(queue empty or all blocked)"


def agent_status():
    rows = []
    for f in sorted((B / "outbox").glob("*.md")):
        name = f.stem
        if name == "conductor":
            continue
        text = f.read_text(encoding="utf-8", errors="replace")
        heads = re.findall(r"^## (.+)$", text, flags=re.M)
        last = heads[-1] if heads else "(no reports)"
        rows.append((name, last))
    return rows


def orphan_scan():
    repo = pathlib.Path("/mnt/c/Agents/agentic-universe/repo/tools/orphan_scan.py")
    if not repo.exists():
        return "(orphan_scan.py not found)"
    return sh(["python3", str(repo), "scan"], timeout=15)


def aether():
    r = sh(["curl", "-s", "--max-time", "2", "-o", "/dev/null", "-w", "%{http_code}",
           "http://127.0.0.1:8317/v1/models"])
    return "UP (from WSL)" if r.strip() == "200" else "not reachable from WSL"


def build():
    wsl_free, win_free = mem()
    g = guard_state()
    nt = next_task()
    agents = agent_status()
    orphans = orphan_scan()
    aeth = aether()
    now = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())

    def esc(s):
        return html.escape(str(s))

    agent_rows = "\n".join(
        "<tr><td class=name>%s</td><td>%s</td></tr>" % (esc(n), esc(last))
        for n, last in agents
    ) or "<tr><td colspan=2>(no agents)</td></tr>"

    doc = """<!doctype html>
<html><head><meta charset="utf-8">
<meta http-equiv="refresh" content="30">
<title>Agentic Universe Fleet</title>
<style>
body{font-family:ui-monospace,Consolas,monospace;background:#0d1117;color:#c9d1d9;margin:0;padding:24px}
h1{color:#58a6ff;font-size:18px;margin:0 0 4px}
.ts{color:#8b949e;font-size:12px;margin-bottom:20px}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:20px}
.card{background:#161b22;border:1px solid #30363d;border-radius:6px;padding:14px}
.card h2{font-size:13px;color:#8b949e;text-transform:uppercase;margin:0 0 8px;letter-spacing:.05em}
.ok{color:#3fb950}.bad{color:#f85149}
table{width:100%;border-collapse:collapse;font-size:13px}
td{padding:4px 8px;border-bottom:1px solid #21262d;vertical-align:top}
.name{color:#58a6ff;font-weight:bold;white-space:nowrap}
pre{white-space:pre-wrap;font-size:12px;margin:0;color:#c9d1d9}
.wide{grid-column:1/-1}
</style></head><body>
<h1>Agentic Universe — Fleet Dashboard</h1>
<div class="ts">generated __NOW__ · auto-refreshes every 30s</div>
<div class="grid">
  <div class="card"><h2>Resources</h2>
    WSL free: __WSL__ MB<br>Windows free: __WIN__ MB<br>
    Guard: <span class="__GCLASS__">__G__</span><br>
    Aether: __AETH__
  </div>
  <div class="card"><h2>Conductor</h2>
    Next queue task: __NT__
  </div>
  <div class="card wide"><h2>Agents (last board report)</h2>
    <table>__ROWS__</table>
  </div>
  <div class="card wide"><h2>Live agy/codex/claude processes (orphan_scan)</h2>
    <pre>__ORPHANS__</pre>
  </div>
</div>
</body></html>"""
    doc = (doc.replace("__NOW__", esc(now)).replace("__WSL__", esc(wsl_free))
           .replace("__WIN__", esc(win_free))
           .replace("__GCLASS__", "ok" if g == "OK" else "bad")
           .replace("__G__", esc(g)).replace("__AETH__", esc(aeth))
           .replace("__NT__", esc(nt)).replace("__ROWS__", agent_rows)
           .replace("__ORPHANS__", esc(orphans)))
    OUT.write_text(doc, encoding="utf-8")
    print("wrote", OUT)


if __name__ == "__main__":
    build()
